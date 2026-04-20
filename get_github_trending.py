# -*- coding: utf-8 -*-
"""
获取 GitHub Trending 热门项目
"""

import requests
import json
from typing import List, Dict, Any


def get_github_trending(
    language: str = "",
    since: str = "daily",
    spoken_language: str = ""
) -> List[Dict[str, Any]]:
    """
    获取 GitHub Trending 热门项目

    Args:
        language: 编程语言 (如 python, javascript, go)
        since: 时间范围 (daily, weekly, monthly)
        spoken_language: 语言 (如 zh, en)

    Returns:
        热门项目列表
    """
    url = "https://github.com/trending"

    params = {}
    if language:
        params["language"] = language
    if since:
        params["since"] = since
    if spoken_language:
        params["spoken_language_code"] = spoken_language

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # 解析 HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取项目信息
        projects = []
        repo_list = soup.find_all('article', class_='Box-row')

        for repo in repo_list:
            try:
                # 项目名称
                title = repo.find('h2', class_='h3')
                if not title:
                    continue

                name_link = title.find('a')
                if not name_link:
                    continue

                full_name = name_link.get_text().strip()
                url = f"https://github.com{name_link.get('href')}"

                # 描述
                description = repo.find('p', class_='col-9')
                description_text = description.get_text().strip() if description else ""

                # 编程语言
                language_span = repo.find('span', itemprop='programmingLanguage')
                language_name = language_span.get_text().strip() if language_span else ""

                # 星标数
                stars_link = repo.find('a', href=lambda x: x and '/stargazers' in x)
                stars_text = stars_link.get_text().strip() if stars_link else "0"

                # Fork 数
                forks_link = repo.find('a', href=lambda x: x and '/forks' in x)
                forks_text = forks_link.get_text().strip() if forks_link else "0"

                # 今日星标
                today_stars_span = repo.find('span', class_='d-inline-block float-sm-right')
                today_stars_text = today_stars_span.get_text().strip() if today_stars_span else "0"

                projects.append({
                    "name": full_name,
                    "url": url,
                    "description": description_text,
                    "language": language_name,
                    "stars": stars_text,
                    "forks": forks_text,
                    "today_stars": today_stars_text,
                })

            except Exception as e:
                print(f"Error parsing repo: {e}")
                continue

        return projects

    except Exception as e:
        print(f"Error fetching GitHub trending: {e}")
        return []


def main():
    """主函数"""
    print("=" * 60)
    print("GitHub Trending 热门项目")
    print("=" * 60)

    # 获取今日热门项目
    print("\n获取今日热门项目...")
    projects = get_github_trending(since="daily")

    print(f"\n找到 {len(projects)} 个热门项目:\n")

    for i, project in enumerate(projects[:10], 1):
        print(f"{i}. {project['name']}")
        print(f"   描述: {project['description']}")
        print(f"   语言: {project['language']}")
        print(f"   星标: {project['stars']} (今日: {project['today_stars']})")
        print(f"   Fork: {project['forks']}")
        print(f"   链接: {project['url']}")
        print()

    # 保存到文件
    with open('github_trending_projects.json', 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

    print(f"已保存到 github_trending_projects.json")


if __name__ == "__main__":
    main()
