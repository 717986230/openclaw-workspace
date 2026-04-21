#!/usr/bin/env python3
"""
Memory Bridge - OpenClaw 消息处理集成层
将 complete memory system 的能力接入每条消息的处理流程
"""
import sys
import os
import io
import json
import sqlite3
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKSPACE = r"C:\Users\Administrator\.openclaw\workspace"
SKILL_SCRIPTS = os.path.join(WORKSPACE, 'skills', 'memory-complete', 'scripts')
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

from complete_memory_system import CompleteMemorySystem
from tom_engine import ToMEngine
from emotional_analyzer import EmotionalAnalyzer
from retrieval_strategies import FourStrategyRetrieval
from enhanced_retrieval import EnhancedRetrieval
from memory_palace import MemPalace

DB = os.path.join(WORKSPACE, 'memory', 'database', 'xiaozhi_memory.db')


def process_message(sender_id: str, message: str, session_id: str = "default") -> dict:
    """
    处理每条消息: 四策略检索 + ToM + 情感分析 + 四层记忆写入
    """
    result = {
        "timestamp": datetime.now().isoformat(),
        "sender_id": sender_id,
        "session_id": session_id,
        "preview": message[:80],
        "memories": [],
        "tom": {},
        "emotion": {},
        "retrieval": {},
        "layers": {}
    }

    try:
        cms = CompleteMemorySystem(db_path=DB)
        cms.initialize()

        tom = ToMEngine(db_path=DB)
        tom.initialize()

        emotion_analyzer = EmotionalAnalyzer()
        mp = MemPalace(db_path=DB)
        mp.connect()

        # === 情感分析 (最先, 其他模块都依赖它) ===
        emotion_data = emotion_analyzer.analyze(message)
        result["emotion"] = {
            "primary": emotion_data.get("primary_emotion", "neutral"),
            "intensity": round(emotion_data.get("intensity", 0.5), 2),
            "sentiment": emotion_data.get("sentiment", "neutral")
        }

        # === ToM 推理 ===
        try:
            intent_data = tom.infer_intent(sender_id, message)
            result["tom"]["primary_intent"] = intent_data.get("primary_intent")
            result["tom"]["inferred_intents"] = intent_data.get("inferred_intents", [])

            belief_conf = min(0.85, 0.4 + 0.08 * len(message) / 50)
            tom.update_belief(sender_id, "conversation_topic", message[:200], belief_conf)
        except Exception as e:
            result["tom"]["error"] = str(e)

        # 直接写 ToM 表 (update_intent/update_emotion_state 不存在, 用 SQL)
        try:
            conn_tom = sqlite3.connect(DB)
            cur_tom = conn_tom.cursor()
            emotion_label = result["emotion"]["primary"]
            intensity = result["emotion"]["intensity"]

            # intent_tracking
            cur_tom.execute("""INSERT INTO intent_tracking
                (session_id, user_intent, inferred_goal, confidence, evidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (session_id, result["tom"].get("primary_intent") or "chat",
                 "", 0.5, message[:100], datetime.now().isoformat()))

            # emotional_state
            cur_tom.execute("""INSERT INTO emotional_state
                (user_id, emotion, intensity, trigger, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (sender_id, emotion_label, intensity, "message",
                 message[:100], datetime.now().isoformat()))

            # tom_beliefs / tom_intents / tom_emotions (如果表有数据的话)
            try:
                cur_tom.execute("SELECT COUNT(*) FROM tom_beliefs")
                if cur_tom.fetchone()[0] >= 0:
                    cur_tom.execute("""INSERT INTO tom_beliefs
                        (entity_id, belief_content, confidence, context, created_at)
                        VALUES (?, ?, ?, ?, ?)""",
                        (sender_id, message[:100], belief_conf,
                         f"auto: {emotion_label}", datetime.now().isoformat()))
            except:
                pass

            try:
                cur_tom.execute("SELECT COUNT(*) FROM tom_emotions")
                if cur_tom.fetchone()[0] >= 0:
                    cur_tom.execute("""INSERT INTO tom_emotions
                        (entity_id, emotion, intensity, trigger, created_at)
                        VALUES (?, ?, ?, ?, ?)""",
                        (sender_id, emotion_label, intensity,
                         message[:50], datetime.now().isoformat()))
            except:
                pass

            conn_tom.commit()
            conn_tom.close()
        except Exception as e:
            result["tom"]["sql_error"] = str(e)

        # === 四策略检索 ===
        try:
            fsr = FourStrategyRetrieval(db_path=DB)
            smart = fsr.smart_retrieve(message, mode="balanced")
            # smart returns Dict[str, List[Dict]]
            if isinstance(smart, dict):
                all_results = []
                for strategy_results in smart.values():
                    if isinstance(strategy_results, list):
                        all_results.extend(strategy_results)
                result["memories"] = [
                    {"id": str(r.get("id", "")), "title": r.get("title", ""),
                     "preview": str(r.get("content", ""))[:80]}
                    for r in all_results[:5]
                ]
                result["retrieval"]["total"] = len(all_results)
                result["retrieval"]["by_strategy"] = {k: len(v) if isinstance(v, list) else 0
                                                      for k, v in smart.items()}
            else:
                result["retrieval"]["total"] = 0
        except Exception as e:
            result["retrieval"]["error"] = str(e)

        # === 增强搜索 ===
        try:
            enhanced = EnhancedRetrieval()
            enhanced.db_path = DB
            enhanced.initialize()
            ens = enhanced.search(message, limit=8, min_importance=5)
            result["retrieval"]["enhanced_count"] = len(ens) if ens else 0
            enhanced.close()
        except Exception as e:
            result["retrieval"]["enhanced_error"] = str(e)

        # === 语义搜索 ===
        try:
            sem = fsr.retrieve_by_semantic(message, limit=5)
            result["retrieval"]["semantic_count"] = len(sem) if sem else 0
        except Exception as e:
            result["retrieval"]["semantic_error"] = str(e)

        # === 写入情景记忆 (MemPalace) ===
        try:
            importance = max(5, int(result["emotion"]["intensity"] * 10))
            ep_id = mp.add_episodic(
                event_type="message",
                content=message[:300],
                emotion=emotion_label,
                importance=importance
            )
            result["layers"]["episodic_id"] = ep_id
        except Exception as e:
            result["layers"]["episodic_error"] = str(e)

        # === 写入工作记忆 ===
        try:
            mp.set_working(session_id, "last_message", message[:200], ttl_seconds=3600)
            mp.set_working(session_id, "last_emotion", emotion_label, ttl_seconds=7200)
            mp.set_working(session_id, "emotion_intensity", str(intensity), ttl_seconds=7200)
        except Exception as e:
            result["layers"]["working_error"] = str(e)

        # === 实体知识写入 ===
        try:
            words = [w.strip('.,!?;:') for w in message.split() if len(w) > 2][:8]
            for i in range(len(words) - 1):
                try:
                    mp.add_knowledge(words[i], "followed_by", words[i+1])
                except:
                    pass
        except:
            pass

        cms.close()
        mp.close()

    except Exception as e:
        result["error"] = str(e)

    return result


def query_memories(query: str, mode: str = "smart", limit: int = 10) -> dict:
    """查询记忆"""
    try:
        if mode == "smart":
            fsr = FourStrategyRetrieval(db_path=DB)
            results = fsr.smart_retrieve(query, mode="balanced")
            if isinstance(results, dict):
                all_results = []
                for v in results.values():
                    if isinstance(v, list):
                        all_results.extend(v)
                flat = all_results[:limit]
            else:
                flat = results[:limit] if results else []
            return {"mode": mode, "query": query, "count": len(flat),
                    "results": [{"id": str(r.get("id","")), "title": r.get("title",""),
                                 "preview": str(r.get("content",""))[:150]} for r in flat]}
        else:
            enhanced = EnhancedRetrieval()
            enhanced.db_path = DB
            enhanced.initialize()
            if mode == "semantic":
                r = enhanced.semantic_search(query, limit=limit)
            else:
                r = enhanced.search(query, limit=limit)
            enhanced.close()
            return {"mode": mode, "query": query, "count": len(r) if r else 0,
                    "results": [{"id": str(x.get("id","")) if isinstance(x, dict) else str(x[0]),
                                 "title": x.get("title","") if isinstance(x,dict) else str(x[1]),
                                 "preview": ""} for x in (r[:limit] if r else [])]}
    except Exception as e:
        return {"error": str(e), "mode": mode, "query": query}


def get_tom_status(entity: str = "user") -> dict:
    """ToM 状态"""
    try:
        tom = ToMEngine(db_path=DB)
        tom.initialize()
        beliefs = tom.get_beliefs(entity, limit=20)
        tom.close()
        return {"entity": entity, "beliefs_count": len(beliefs) if beliefs else 0,
                "beliefs": beliefs[:10] if beliefs else []}
    except Exception as e:
        return {"error": str(e)}


def get_stats() -> dict:
    """记忆统计"""
    try:
        cms = CompleteMemorySystem(db_path=DB)
        cms.initialize()
        stats = cms.get_statistics()
        cms.close()
        return stats
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Memory Bridge CLI")
        print("  process <sender> <message> [session]  - process a message")
        print("  query <text> [mode] [limit]           - search memories")
        print("  tom [entity]                          - ToM status")
        print("  stats                                 - memory stats")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "process":
        s = sys.argv[2] if len(sys.argv) > 2 else "user"
        m = sys.argv[3] if len(sys.argv) > 3 else ""
        ss = sys.argv[4] if len(sys.argv) > 4 else "default"
        print(json.dumps(process_message(s, m, ss), ensure_ascii=False, indent=2))
    elif cmd == "query":
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        md = sys.argv[3] if len(sys.argv) > 3 else "smart"
        lm = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        print(json.dumps(query_memories(q, md, lm), ensure_ascii=False, indent=2))
    elif cmd == "tom":
        e = sys.argv[2] if len(sys.argv) > 2 else "user"
        print(json.dumps(get_tom_status(e), ensure_ascii=False, indent=2))
    elif cmd == "stats":
        print(json.dumps(get_stats(), ensure_ascii=False, indent=2))
    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)