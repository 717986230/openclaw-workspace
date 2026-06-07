#!/usr/bin/env python3
"""
蜂群研究员 - 处理蚁群采集的数据，提炼关键洞察
"""
import json
from datetime import datetime
from typing import List, Dict, Any


def summarize_findings(findings: List[str], source_name: str) -> Dict:
    """对单个来源的发现做简单提炼"""
    if not findings:
        return {"source": source_name, "insights": [], "count": 0}

    insights = []
    for f in findings[:5]:
        text = f.strip().lstrip("📰").strip()
        if len(text) > 10:
            insights.append(text[:120])

    return {"source": source_name, "insights": insights, "count": len(insights)}


def run_researcher(collector_result: Dict = None) -> Dict:
    """运行蜂群研究员，处理采集结果"""
    print(f"\n🐝 蜂群研究员启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not collector_result or "ants" not in collector_result:
        print("   ⚠️ 无采集数据，使用空结果")
        return {"total": 0, "summaries": [], "report": "无可用采集数据"}

    ants = collector_result.get("ants", [])
    summaries = []

    for ant_result in ants:
        ant_name = ant_result.get("ant", "未知蚂蚁")
        findings = ant_result.get("findings", [])
        summary = summarize_findings(findings, ant_name)
        summaries.append(summary)
        print(f"   🔍 {ant_name}: 提炼 {summary['count']} 条洞察")

    total_insights = sum(s["count"] for s in summaries)

    # 生成简短报告
    report_lines = [f"📊 研究报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    for s in summaries:
        if s["insights"]:
            report_lines.append(f"\n【{s['source']}】")
            for insight in s["insights"][:3]:
                report_lines.append(f"  • {insight}")

    report = "\n".join(report_lines)

    print(f"   ✅ 研究完成，共提炼 {total_insights} 条洞察")
    return {
        "total": total_insights,
        "summaries": summaries,
        "report": report,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # 测试：用模拟数据运行
    mock_collector = {
        "ants": [
            {
                "ant": "新闻蚂蚁",
                "findings": ["📰 Tech layoffs continue at major firms", "📰 AI funding hits record high in Q2"]
            },
            {
                "ant": "期货蚂蚁",
                "findings": ["📰 Oil prices surge on OPEC decision", "📰 Gold hits 3-month high"]
            }
        ]
    }
    result = run_researcher(mock_collector)
    print(json.dumps(result, ensure_ascii=False, indent=2))
