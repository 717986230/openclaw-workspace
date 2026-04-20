# -*- coding: utf-8 -*-
"""
搜索 GitHub 专业智能体项目 - Search GitHub Professional Agent Projects
从 GitHub 搜索专业的 AI 智能体项目
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Any
from datetime import datetime


def search_github_agents(query: str = "AI agents prompts", max_results: int = 10) -> List[Dict[str, Any]]:
    """搜索 GitHub 上的智能体项目"""
    print(f"Searching GitHub for: {query}")

    # GitHub 搜索 URL
    url = f"https://github.com/search?q={query}&type=repositories"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 解析搜索结果
        results = []
        repo_items = soup.find_all('div', class_='repo-list-item')

        for i, item in enumerate(repo_items[:max_results]):
            try:
                # 提取仓库信息
                name_elem = item.find('a', class_='v-align-middle')
                if not name_elem:
                    continue

                name = name_elem.text.strip()
                url = f"https://github.com{name_elem['href']}"

                # 提取描述
                desc_elem = item.find('p', class_='mb-1')
                description = desc_elem.text.strip() if desc_elem else ""

                # 提取语言
                lang_elem = item.find('span', itemprop='programmingLanguage')
                language = lang_elem.text.strip() if lang_elem else ""

                # 提取星标数
                stars_elem = item.find('a', class_='Link--muted d-inline-block mr-3')
                stars = stars_elem.text.strip() if stars_elem else "0"

                results.append({
                    "name": name,
                    "url": url,
                    "description": description,
                    "language": language,
                    "stars": stars,
                })

                print(f"  {i+1}. {name} ({stars} stars)")

            except Exception as e:
                print(f"  Error parsing item: {e}")
                continue

        return results

    except Exception as e:
        print(f"Error searching GitHub: {e}")
        return []


def search_specific_repos() -> List[Dict[str, Any]]:
    """搜索特定的知名智能体仓库"""
    print("Searching specific agent repositories...")

    # 已知的优质智能体仓库
    repos = [
        {
            "name": "microsoft/prompt-engine",
            "url": "https://github.com/microsoft/prompt-engine",
            "description": "Microsoft's prompt engineering library",
            "language": "TypeScript",
            "stars": "N/A",
        },
        {
            "name": "dair-ai/Prompt-Engineering-Guide",
            "url": "https://github.com/dair-ai/Prompt-Engineering-Guide",
            "description": "Comprehensive prompt engineering guide",
            "language": "Markdown",
            "stars": "N/A",
        },
        {
            "name": "f/awesome-chatgpt-prompts",
            "url": "https://github.com/f/awesome-chatgpt-prompts",
            "description": "Awesome ChatGPT prompts collection",
            "language": "Markdown",
            "stars": "N/A",
        },
        {
            "name": "microsoft/semantic-kernel",
            "url": "https://github.com/microsoft/semantic-kernel",
            "description": "Microsoft's AI orchestration SDK",
            "language": "Python",
            "stars": "N/A",
        },
        {
            "name": "langchain-ai/langchain",
            "url": "https://github.com/langchain-ai/langchain",
            "description": "LangChain framework for LLM applications",
            "language": "Python",
            "stars": "N/A",
        },
        {
            "name": "openai/openai-cookbook",
            "url": "https://github.com/openai/openai-cookbook",
            "description": "OpenAI cookbook with examples",
            "language": "Python",
            "stars": "N/A",
        },
        {
            "name": "anthropics/anthropic-cookbook",
            "url": "https://github.com/anthropics/anthropic-cookbook",
            "description": "Anthropic cookbook with examples",
            "language": "Python",
            "stars": "N/A",
        },
        {
            "name": "deepseek-ai/DeepSeek-Coder",
            "url": "https://github.com/deepseek-ai/DeepSeek-Coder",
            "description": "DeepSeek code generation models",
            "language": "Python",
            "stars": "N/A",
        },
        {
            "name": "QwenLM/Qwen-Agent",
            "url": "https://github.com/QwenLM/Qwen-Agent",
            "description": "Qwen agent framework",
            "language": "Python",
            "stars": "N/A",
        },
        {
            "name": "THUDM/ChatGLM",
            "url": "https://github.com/THUDM/ChatGLM",
            "description": "ChatGLM language models",
            "language": "Python",
            "stars": "N/A",
        },
    ]

    for i, repo in enumerate(repos):
        print(f"  {i+1}. {repo['name']}")

    return repos


def main():
    """主函数"""
    print("=" * 60)
    print("GitHub Professional Agent Projects Search")
    print("=" * 60)

    # 搜索特定仓库
    print("\n[1] Searching specific agent repositories...")
    specific_repos = search_specific_repos()

    # 搜索 GitHub
    print("\n[2] Searching GitHub for agent projects...")
    github_results = search_github_agents("AI agents prompts", max_results=10)

    # 合并结果
    all_results = specific_repos + github_results

    # 保存结果
    output_file = "github_agent_projects.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "search_time": datetime.now().isoformat(),
            "total_results": len(all_results),
            "results": all_results,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[3] Results saved to: {output_file}")
    print(f"    Total projects found: {len(all_results)}")

    print("\n" + "=" * 60)
    print("Search completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
