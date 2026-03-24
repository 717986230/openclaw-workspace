#!/usr/bin/env python3
"""
期货多维度综合分析脚本
功能：结合供需、宏观、资金、技术、地缘、政策等多维度分析
"""

import json
from datetime import datetime
from collections import defaultdict

# ============================================================
# 📊 多维度因子分析框架
# ============================================================

FACTORS = {
    "原油": {
        "supply": {
            "OPEC+减产": 8, "页岩油增产": -6, "全球产能": -4,
            "库存偏低": 6, "库存累积": -5, "伊朗制裁": 5
        },
        "demand": {
            "全球经济放缓": -8, "中国需求": 5, "新能源替代": -4,
            "航运行情": 4, "工业需求": 3
        },
        "macro": {
            "美联储加息": -7, "美元反弹": -6, "通胀预期": 5,
            "中国经济刺激": 4
        },
        "geo": {
            "中东战争": 10, "俄乌冲突": 6, "美伊谈判": -8,
            "地缘缓和": -7
        },
        "funds": {
            "多头增仓": 5, "空头增仓": -5, "基金净多": 4,
            "期货升水": -3, "期货贴水": 3
        },
        "tech": {
            "突破新高": 4, "跌破均线": -4, "MACD金叉": 3,
            "RSI超买": -3, "布林上轨": -2
        },
        "policy": {
            "战略储备释放": -5, "收储": 4, "环保政策": 3
        }
    },
    "白银": {
        "supply": {
            "矿产减产": 5, "回收增加": -2, "库存偏高": -4
        },
        "demand": {
            "光伏需求": 6, "电子需求": 4, "珠宝需求": 3,
            "投资需求": 5
        },
        "macro": {
            "美元反弹": -7, "实际利率下行": 6, "通胀": 5
        },
        "geo": {
            "避险需求": 7, "地缘风险": 5
        },
        "funds": {
            "ETF流入": 5, "期货净多": 4
        },
        "tech": {
            "突破新高": 4, "均线多头": 3
        },
        "policy": {
            "央行购金": 5
        }
    },
    "黄金": {
        "supply": {
            "矿产稳定": 0, "回收增加": -1
        },
        "demand": {
            "央行购金": 8, "珠宝需求": 3, "投资需求": 5
        },
        "macro": {
            "美元反弹": -8, "实际利率下行": 8, "美联储降息": 7
        },
        "geo": {
            "避险需求": 10, "战争风险": 8, "经济不确定性": 6
        },
        "funds": {
            "ETF流入": 6, "期货净多": 5, "空头回补": 4
        },
        "tech": {
            "突破新高": 5, "站上均线": 3
        },
        "policy": {
            "央行购金": 8, "货币宽松": 6
        }
    },
    "铜": {
        "supply": {
            "矿端紧张": 7, "新增产能": -5, "罢工影响": 4
        },
        "demand": {
            "新能源需求": 8, "房地产低迷": -6, "电网投资": 5,
            "出口需求": 4
        },
        "macro": {
            "中国经济": 8, "美元": -3
        },
        "geo": {"智利局势": 4},
        "funds": {
            "库存下降": 5, "期货升水": 4
        },
        "tech": {
            "跌破均线": -4
        },
        "policy": {
            "基建刺激": 6, "房地产政策": 5
        }
    },
    "铝": {
        "supply": {
            "矿端紧张": 6, "电解铝产能": -4, "西南限电": 5
        },
        "demand": {
            "新能源需求": 6, "房地产低迷": -5, "汽车需求": 4
        },
        "macro": {"中国需求": 7},
        "geo": {"几内亚发运": 5},
        "funds": {
            "期货升水300": -5, "库存偏低": 6
        },
        "tech": {},
        "policy": {
            "电解铝高利润": 5
        }
    },
    "铁矿石": {
        "supply": {
            "发运增加": -6, "发运减少": 6, "港口库存低": 5
        },
        "demand": {
            "钢材需求弱": -6, "钢材需求好": 6, "压产政策": -5
        },
        "macro": {"中国钢铁": 8},
        "geo": {},
        "funds": {
            "港口库存": 5
        },
        "tech": {},
        "policy": {
            "粗钢压产": -6
        }
    },
    "螺纹钢": {
        "supply": {
            "产能过剩": -6, "开工率低": 4
        },
        "demand": {
            "房地产差": -8, "基建投资": 6, "制造业": 4
        },
        "macro": {"中国房地产": 10},
        "geo": {},
        "funds": {
            "库存下降": 4
        },
        "tech": {},
        "policy": {
            "房产松绑": 7, "基建刺激": 6
        }
    },
    "燃料油": {
        "supply": {},
        "demand": {"航运需求": 5, "发电需求": 4},
        "macro": {"原油成本": 10},
        "geo": {},
        "funds": {},
        "tech": {},
        "policy": {}
    },
    # 化工品种
    "PTA": {
        "supply": {"装置检修": 4, "新产能投放": -6, "开工率高": -4},
        "demand": {"聚酯需求": 6, "纺织旺季": 5, "出口": 3},
        "macro": {"原油成本": 8, "PX成本": 6},
        "geo": {},
        "funds": {"期货升水": -3},
        "tech": {},
        "policy": {}
    },
    "甲醇": {
        "supply": {"西南限气": 4, "新增产能": -5, "进口增加": -4},
        "demand": {"MTO需求": 6, "传统需求": 3},
        "macro": {"煤炭成本": 6},
        "geo": {},
        "funds": {},
        "tech": {},
        "policy": {}
    },
    "PVC": {
        "supply": {"电石供应": 5, "新增产能": -4, "检修": 3},
        "demand": {"房地产": -6, "基建": 5, "出口": 4},
        "macro": {"电石成本": 5},
        "geo": {},
        "funds": {},
        "tech": {},
        "policy": {}
    },
    "PP": {
        "supply": {"检修": 4, "新产能": -5, "进口": -2},
        "demand": {"汽车需求": 4, "家电": 3, "包装": 3},
        "macro": {"丙烯成本": 5},
        "geo": {},
        "funds": {},
        "tech": {},
        "policy": {}
    },
    "塑料": {
        "supply": {"检修": 4, "新产能": -5},
        "demand": {"农膜": 4, "包装": 3, "汽车": 3},
        "macro": {"乙烯成本": 5},
        "geo": {},
        "funds": {},
        "tech": {},
        "policy": {}
    },
    "尿素": {
        "supply": {"检修": 3, "日产量高": -4, "出口": 4},
        "demand": {"春耕": 6, "工业需求": 3},
        "macro": {"煤炭成本": 5},
        "geo": {},
        "funds": {},
        "tech": {},
        "policy": {"保供": -3}
    }
}

# 新闻影响系数（从实际新闻动态调整）
NEWS_IMPACT = {
    "原油": {
        "特朗普谈判": -10, "美伊冲突": 10, "OPEC减产": 8,
        "原油大跌": -8, "原油大涨": 8
    },
    "白银": {
        "贵金属大跌": -8, "避险需求": 7
    }
}

def get_current_factors(commodity):
    """获取品种当前影响因素（可从外部动态更新）"""
    # 这里可以接入实时新闻API
    # 目前使用静态因子库
    return FACTORS.get(commodity, {})

def calculate_dimension_score(factors_dict):
    """计算单维度得分"""
    if not factors_dict:
        return 50
    score = 50
    for factor, weight in factors_dict.items():
        score += weight
    return max(20, min(80, score))

def analyze_commodity(commodity, news_impact=None):
    """综合分析单个品种"""
    factors = get_current_factors(commodity)
    
    if not factors:
        return None
    
    # 各维度得分（简化）
    dimension_scores = {}
    dimension_weights = {
        "supply": 0.25, "demand": 0.25, "macro": 0.15,
        "geo": 0.15, "funds": 0.10, "tech": 0.05, "policy": 0.05
    }
    
    for dim, weight in dimension_weights.items():
        dim_factors = factors.get(dim, {})
        score = calculate_dimension_score(dim_factors)
        dimension_scores[dim] = score
        if score >= 55:
            indicator = "↑"
        elif score <= 45:
            indicator = "↓"
        else:
            indicator = "→"
        dimension_scores[f"{dim}_ind"] = indicator
    
    # 加权总分
    total_score = sum(
        dimension_scores[dim] * weight 
        for dim, weight in dimension_weights.items()
    )
    
    # 新闻影响
    if news_impact:
        total_score += news_impact
    
    total_score = max(20, min(80, total_score))
    
    # 趋势判断
    if total_score >= 60:
        trend = "🟢 多方占优"
    elif total_score <= 40:
        trend = "🔴 空方占优"
    else:
        trend = "🟡 震荡"
    
    # 关键因素
    all_factors = []
    for dim, factors_dict in factors.items():
        for f, w in factors_dict.items():
            if w > 0:
                all_factors.append((f"{dim}:{f}", w))
            elif w < 0:
                all_factors.append((f"{dim}:{f}", w))
    
    top_factors = sorted(all_factors, key=lambda x: abs(x[1]), reverse=True)[:5]
    
    return {
        "commodity": commodity,
        "score": round(total_score, 1),
        "trend": trend,
        "dimensions": dimension_scores,
        "top_factors": top_factors
    }

def analyze_all(commodities=None):
    """分析所有品种"""
    if commodities is None:
        commodities = list(FACTORS.keys())
    
    results = []
    for c in commodities:
        result = analyze_commodity(c)
        if result:
            results.append(result)
    
    # 按得分排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def format_report(commodity=None, news_impact=None):
    """格式化报告输出"""
    if commodity:
        result = analyze_commodity(commodity, news_impact)
        if not result:
            return f"❌ 不支持的品种: {commodity}"
        
        # 简化输出
        score = result['score']
        trend = result['trend'].split()[1]
        
        # 关键因素一句话
        key_factors = []
        for f, w in result['top_factors'][:3]:
            name = f.split(":")[1]
            key_factors.append(f"{'+' + str(w) if w > 0 else str(w)} {name}")
        
        emoji = "📈" if score >= 55 else "📉" if score <= 45 else "➡️"
        report = f"{emoji} {result['commodity']} {score}分 {trend}\n关键: {', '.join(key_factors)}\n建议: 等待企稳"
        
        return report
    else:
        # 汇总分析
        results = analyze_all()
        
        # 简化为：品种 方向 关键一句话
        report = f"📊 {datetime.now().strftime('%m-%d %H:%M')}\n"
        for r in results:
            emoji = "📈" if r['score'] >= 55 else "📉" if r['score'] <= 45 else "➡️"
            # 取最关键的一个因素
            key = r['top_factors'][0][0].split(":")[1] if r['top_factors'] else ""
            report += f"{emoji} {r['commodity']} {key}\n"
        
        return report

def main():
    import sys
    args = sys.argv[1:]
    
    if not args or args[0] in ["--all", "-a"]:
        print(format_report())
    elif args[0] == "--help":
        print("""
📖 用法：
  python futures_analysis.py           # 分析所有品种
  python futures_analysis.py --all     # 同上
  python futures_analysis.py 原油      # 单品种分析
  python futures_analysis.py --help    # 帮助

📋 支持品种：
  原油、白银、黄金、铜、铝、铁矿石、螺纹钢、燃料油
""")
    else:
        commodity = args[0]
        news = None
        # 检查是否有新闻影响参数
        if len(args) > 1:
            try:
                news = float(args[1])
            except:
                pass
        print(format_report(commodity, news))

if __name__ == "__main__":
    main()