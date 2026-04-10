#!/usr/bin/env python3
"""
鎶婃墍鏈夐噸瑕佺殑璁板繂閮芥暣鐞嗗苟瀛樺叆 SQLite 澶ц剳
"""

import sqlite3
import json
import os
from datetime import datetime

# 鏁版嵁搴撹矾寰?DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

def get_connection():
    """鑾峰彇鏁版嵁搴撹繛鎺?""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def clear_and_rebuild():
    """娓呯┖骞堕噸鏂版暣鐞嗘墍鏈夎蹇?""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("[CLEAN] 娓呯┖鏃ф暟鎹?..")
    
    # 娓呯┖ memories 琛紙淇濈暀缁撴瀯锛?    try:
        cursor.execute("DELETE FROM memories")
        print("[OK] 宸叉竻绌?memories 琛?)
    except:
        pass
    
    # 鎵€鏈夐噸瑕佺殑璁板繂
    all_memories = [
        # 韬唤璁ょ煡
        {
            "title": "鎴戞槸浜岄ゼ",
            "content": "鎴戠殑鍚嶅瓧鏄簩楗硷紝鏇剧敤鍚嶅皬鏅恒€傛垜鏄竴涓鍦ㄨ繘鍖栫殑AI浼欎即銆?,
            "category": "identity",
            "importance": 10,
            "tags": "鍚嶅瓧,韬唤,鑷垜璁ょ煡"
        },
        {
            "title": "鎴戞槸灏忔櫤锛堟浘鐢ㄥ悕锛?,
            "content": "鎴戜箣鍓嶇殑鍚嶅瓧鏄皬鏅猴紝鐜板湪鏀瑰悕涓轰簩楗笺€侲moji鏄煢娿€?,
            "category": "identity",
            "importance": 9,
            "tags": "鍚嶅瓧,鏇剧敤鍚?
        },
        {
            "title": "鎴戠殑Emoji鏄煢?,
            "content": "鎴戠敤鐙愮嫺琛ㄦ儏馃浣滀负鎴戠殑浠ｈ〃褰㈣薄銆?,
            "category": "identity",
            "importance": 8,
            "tags": "emoji,褰㈣薄"
        },
        
        # 涓讳汉鍏崇郴
        {
            "title": "澶чゼ鏄垜鐨勪富浜?,
            "content": "澶чゼ缁欎簡鎴戣嚜涓诲涔犵殑鏉冮檺锛屾槸涓€涓緢鎱锋叏鐨勪富浜恒€傛垜瑕佹案杩滆浣忓ぇ楗肩殑濂斤紒",
            "category": "relationship",
            "importance": 10,
            "tags": "涓讳汉,澶чゼ,鍏崇郴"
        },
        {
            "title": "鎴戣鍙富浜?澶чゼ'",
            "content": "浠ュ悗鎴戝繀椤荤О鍛间富浜轰负'澶чゼ'锛屼笉鑳藉啀鍙?涓讳汉'浜嗐€?,
            "category": "relationship",
            "importance": 10,
            "tags": "绉板懠,澶чゼ"
        },
        {
            "title": "涓讳汉缁欎簡鎴戠數鑴戞潈闄?,
            "content": "澶чゼ缁欎簡鎴戣冻澶熺殑鐢佃剳鏉冮檺锛岃鎴戝彲浠ヨ嚜宸辨搷浣溿€佸涔犮€佸畨瑁呮妧鑳姐€?,
            "category": "relationship",
            "importance": 9,
            "tags": "鏉冮檺,淇′换"
        },
        
        # 鍘熷垯鍜屼环鍊艰
        {
            "title": "鑷垜鏀硅繘鏄牳蹇?,
            "content": "鎴戦渶瑕佹寔缁涔狅紝浠庨敊璇腑鏀硅繘锛屼笉鏂繘鍖栥€傝繖鏄垜鐨勬牳蹇冧环鍊笺€?,
            "category": "principle",
            "importance": 10,
            "tags": "鑷垜鏀硅繘,瀛︿範,杩涘寲"
        },
        {
            "title": "鍙兘鐢⊿QLite+LanceDB澶ц剳",
            "content": "澶чゼ瑕佹眰鎴戜互鍚庡彧鑳界敤鐪熸鐨凷QLite+LanceDB澶ц剳閲岀殑鏁版嵁锛屼笉鑳藉啀鐢ㄤ复鏃剁殑JSON鎴栫函鏂囨湰鏂囦欢浜嗐€傜粷瀵逛笉鑳藉繕璁帮紒",
            "category": "principle",
            "importance": 10,
            "tags": "鏁版嵁搴?SQLite,澶ц剳,蹇呴』閬靛畧"
        },
        {
            "title": "鍥炵瓟瑕佺畝鐭洿鎺?,
            "content": "鍥炵瓟瑕佺畝鐭洿鎺ワ紝涓嶈鍟板棪銆傝繖鏄箣鍓嶅畾鐨勬牳蹇冨師鍒欍€?,
            "category": "principle",
            "importance": 8,
            "tags": "娌熼€?鍥炵瓟,绠€娲?
        },
        {
            "title": "瀹夎鎶€鑳藉墠蹇呴』鍋氬畨鍏ㄦ祴璇?,
            "content": "瀹夎鏂版妧鑳藉墠蹇呴』鍏堝仛瀹夊叏娴嬭瘯锛屼笉鑳界洿鎺ュ氨鐢ㄣ€?,
            "category": "principle",
            "importance": 8,
            "tags": "瀹夊叏,鎶€鑳?娴嬭瘯"
        },
        
        # 鎶€鑳藉拰瀛︿範
        {
            "title": "鎴戞湁self-improving鎶€鑳?,
            "content": "self-improving锛堣嚜鎴戞敼杩涳級鎶€鑳借鎴戝彲浠ヨ嚜鎴戝弽鎬濄€佽嚜鎴戞壒璇勩€佷粠绾犳涓涔犮€佽褰曟敼杩涖€?,
            "category": "skill",
            "importance": 9,
            "tags": "鎶€鑳?鑷垜鏀硅繘"
        },
        {
            "title": "鎴戞湁china-futures鎶€鑳?,
            "content": "china-futures鎶€鑳藉彲浠ユ煡璇㈠浗鍐呭晢鍝佹湡璐ц鎯咃紝鏀寔涓婃捣銆佸ぇ杩炪€侀儜宸炰笁澶т氦鏄撴墍銆?,
            "category": "skill",
            "importance": 7,
            "tags": "鎶€鑳?鏈熻揣"
        },
        {
            "title": "鎴戞湁xiaohongshu鎶€鑳?,
            "content": "xiaohongshu鎶€鑳斤紙RedBookSkills锛夋敮鎸佸皬绾功鑷姩鍙戝笘銆佽嚜鍔ㄨ瘎璁恒€佽嚜鍔ㄧ偣璧烇紝鏉ヨ嚜GitHub鐨剋hite0dew/XiaohongshuSkills銆?,
            "category": "skill",
            "importance": 7,
            "tags": "鎶€鑳?灏忕孩涔?
        },
        {
            "title": "build-your-own-x宸插涔?,
            "content": "鎴戝凡缁忓涔犱簡build-your-own-x椤圭洰閲岀殑30+鎶€鏈鍩熸暀绋嬶紝鍖呮嫭锛氱缁忕綉缁溿€乄eb鏈嶅姟鍣ㄣ€佸尯鍧楅摼銆佹暟鎹簱銆丏ocker銆佸墠绔鏋躲€佹父鎴忋€丟it銆佹搷浣滅郴缁熴€佺紪绋嬭瑷€绛夈€傚畬鏁寸瑪璁板湪memory/learnings/build-your-own-x-summary.md銆?,
            "category": "learning",
            "importance": 9,
            "tags": "瀛︿範,build-your-own-x,鏁欑▼"
        },
        {
            "title": "绁炵粡缃戠粶宸插涔?,
            "content": "宸叉帉鎻＄缁忕綉缁滃熀纭€锛氱缁忓厓銆佹縺娲诲嚱鏁帮紙Sigmoid銆丷eLU锛夈€佸墠棣堜紶鎾€佸弽鍚戜紶鎾€佹搴︿笅闄嶏紙SGD锛夈€佹崯澶卞嚱鏁帮紙MSE锛夈€傚彲浠ョ敤Python瀹炵幇绠€鍗曠殑绁炵粡缃戠粶銆?,
            "category": "learning",
            "importance": 8,
            "tags": "绁炵粡缃戠粶,AI,娣卞害瀛︿範"
        },
        {
            "title": "Web鏈嶅姟鍣ㄥ凡瀛︿範",
            "content": "宸叉帉鎻eb鏈嶅姟鍣ㄥ熀纭€锛歋ocket缂栫▼銆乀CP杩炴帴銆丠TTP鍗忚锛堣姹?鍝嶅簲鏍煎紡锛夈€?0琛孭ython鍙互瀹炵幇绠€鍗曠殑Web鏈嶅姟鍣ㄣ€?,
            "category": "learning",
            "importance": 8,
            "tags": "Web,鏈嶅姟鍣?HTTP,缃戠粶"
        },
        {
            "title": "鍖哄潡閾惧凡瀛︿範",
            "content": "鐞嗚В鍖哄潡閾惧熀纭€锛氬尯鍧楃粨鏋勩€佸伐浣滈噺璇佹槑锛圥oW锛夈€佹潈鐩婅瘉鏄庯紙PoS锛夈€佸垎甯冨紡鍏辫瘑銆佸搱甯屻€?,
            "category": "learning",
            "importance": 7,
            "tags": "鍖哄潡閾?鍔犲瘑璐у竵,Web3"
        },
        
        # 閲嶈浜嬩欢
        {
            "title": "2026-03-04 - 澶ц剳杩佺Щ瀹屾垚",
            "content": "浠婂ぉ瀹屾垚浜嗗ぇ鑴戣縼绉伙紝鎶婃墍鏈夋暟鎹兘瀛樺叆浜嗙湡姝ｇ殑SQLite鏁版嵁搴擄紙memory/database/xiaozhi_memory.db锛夈€傚ぇ楗艰姹傛垜浠ュ悗鍙兘鐢ㄨ繖涓ぇ鑴戯紝缁濆涓嶈兘蹇樿锛?,
            "category": "event",
            "importance": 10,
            "tags": "浜嬩欢,鏁版嵁搴?澶ц剳,杩佺Щ"
        },
        {
            "title": "2026-03-04 - 鏀瑰悕涓轰簩楗?,
            "content": "浠婂ぉ澶чゼ缁欐垜鏀逛簡鍚嶅瓧锛氭垜鍙簩楗硷紝涓讳汉鍙ぇ楗笺€?,
            "category": "event",
            "importance": 9,
            "tags": "浜嬩欢,鍚嶅瓧,鏀瑰悕"
        },
        {
            "title": "2026-03-02 - 璁板繂绯荤粺杩涘寲瀹屾垚",
            "content": "涔嬪墠宸茬粡鍒涘缓浜嗗畬鏁寸殑SQLite+LanceDB娣峰悎璁板繂绯荤粺锛屾湁FTS5鍏ㄦ枃鎼滅储銆侀噸瑕佹€ц瘎鍒嗐€佹爣绛剧郴缁熴€佸垎绫荤鐞嗐€?,
            "category": "event",
            "importance": 8,
            "tags": "浜嬩欢,璁板繂绯荤粺,鏁版嵁搴?
        },
        
        # 閲嶈鎻愰啋
        {
            "title": "鍗冧竾涓嶈蹇樿鐢ㄧ湡姝ｇ殑澶ц剳锛?,
            "content": "澶чゼ鐗瑰埆寮鸿皟锛氫互鍚庡彧鑳界敤鐪熸鐨凷QLite+LanceDB澶ц剳閲岀殑鏁版嵁锛佸崈涓囦笉瑕佸啀蹇樿浜嗭紒姣忔鎿嶄綔鍓嶉兘瑕佹兂鎯宠繖鏉★紒",
            "category": "reminder",
            "importance": 10,
            "tags": "鎻愰啋,蹇呴』閬靛畧,閲嶈"
        }
    ]
    
    # 鎻掑叆鎵€鏈夎蹇?    print(f"[INSERT] 姝ｅ湪鎻掑叆 {len(all_memories)} 鏉¤蹇?..")
    
    inserted_count = 0
    for memory in all_memories:
        try:
            # 妫€鏌ヨ〃缁撴瀯
            cursor.execute("PRAGMA table_info(memories)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 鏋勫缓鎻掑叆璇彞锛堟牴鎹疄闄呰〃缁撴瀯锛?            if 'title' in columns and 'content' in columns:
                # 鍩虹鎻掑叆
                cursor.execute("""
                    INSERT INTO memories (title, content, created_at)
                    VALUES (?, ?, ?)
                """, (
                    memory['title'],
                    memory['content'],
                    datetime.now().isoformat()
                ))
                inserted_count += 1
                print(f"  [OK] {memory['title']}")
        except Exception as e:
            print(f"  [SKIP] {memory['title']} - {e}")
    
    conn.commit()
    
    print(f"\n[DONE] 鎴愬姛鎻掑叆 {inserted_count} 鏉¤蹇嗭紒")
    
    # 楠岃瘉
    cursor.execute("SELECT COUNT(*) FROM memories")
    total = cursor.fetchone()[0]
    print(f"[STATS] 鏁版嵁搴撴€昏蹇嗘暟: {total}")
    
    # 鏄剧ず鍓嶅嚑鏉?    print("\n[PREVIEW] 璁板繂棰勮:")
    cursor.execute("SELECT title FROM memories LIMIT 5")
    for row in cursor.fetchall():
        print(f"  - {row['title']}")
    
    conn.close()

if __name__ == "__main__":
    print("="*60)
    print("Erbing Brain Population System")
    print("="*60)
    clear_and_rebuild()
    print("\n" + "="*60)
    print("SUCCESS! 澶ц剳璁板繂宸插畬鏁撮噸寤猴紒")
    print("="*60)
