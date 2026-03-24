#!/usr/bin/env python3
"""
期货资讯查询脚本
用法: python futures_news.py [--symbol SYMBOL] [--limit N]
示例:
  python futures_news.py                      # 默认查询原油
  python futures_news.py --symbol PTA         # 查询PTA
  python futures_news.py --symbol 黄金        # 查询黄金
  python futures_news.py --limit 5             # 只显示5条
"""
import argparse
from datetime import datetime

# 期货品种搜索映射
SYMBOL_MAP = {
    "原油": "WTI原油期货",
    "WTI": "WTI原油期货",
    "布伦特": "布伦特原油期货",
    "PTA": "PTA期货",
    "螺纹钢": "螺纹钢期货",
    "沪铜": "沪铜期货",
    "沪铝": "沪铝期货",
    "黄金": "黄金期货",
    "白银": "白银期货",
    "豆粕": "豆粕期货",
    "白糖": "白糖期货",
    "棉花": "棉花期货",
    "IF": "沪深300股指期货",
    "IM": "中证1000股指期货",
}


def search_news(query: str, count: int = 10) -> list:
    """搜索新闻"""
    try:
        from ddgs import DDGS
        ddgs = DDGS()
        results = list(ddgs.news(query, max_results=count))
        return results
    except Exception as e:
        print(f"搜索出错: {e}")
        return []


def format_news(results: list, symbol: str):
    """格式化打印新闻"""
    print(f"\n📰 {symbol} 期货资讯")
    print("=" * 60)
    
    if not results:
        print("暂无新闻")
        return
    
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        source = r.get("source", "")
        date = r.get("date", "")[:10] if r.get("date") else ""
        
        print(f"\n{i}. {title}")
        if source:
            print(f"   📌 来源: {source}")
        if date:
            print(f"   🕐 时间: {date}")


def main():
    parser = argparse.ArgumentParser(
        description="期货资讯查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--symbol", "-s", default="原油", 
                        help="期货品种 (默认: 原油)")
    parser.add_argument("--limit", "-l", type=int, default=10, 
                        help="新闻条数 (默认: 10)")
    
    args = parser.parse_args()
    
    # 标准化品种名称
    symbol = SYMBOL_MAP.get(args.symbol, args.symbol)
    search_term = f"{symbol} 2026"
    
    print(f"\n🕐 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📌 查询品种: {symbol}")
    print(f"🔍 搜索关键词: {search_term}")
    
    # 搜索新闻
    print("\n📡 正在搜索新闻...")
    results = search_news(search_term, args.limit)
    
    if results:
        format_news(results, symbol)
    else:
        print("未找到相关新闻")
    
    print("\n" + "=" * 60)
    print("✅ 查询完成")


if __name__ == "__main__":
    main()