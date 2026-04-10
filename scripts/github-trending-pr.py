#!/usr/bin/env python3
"""
GitHub Trending PR Automation System
自动发现热门项目，分析并提交 PR

Phase 1: Discovery - 发现热门项目
Phase 2: Analysis - 分析项目结构
Phase 3: Contribution - 寻找贡献机会
Phase 4: Execution - 执行 PR
"""

import subprocess
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db")

class GitHubTrendingPR:
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row

    def discover_trending(self, language="python", since="daily"):
        """Phase 1: Discover trending repositories"""
        print(f"=== Phase 1: Discovering trending {language} repos ===")

        # Use gh CLI to get trending (JSON output to avoid encoding issues)
        cmd = f'gh search repos --language={language} --sort=stars --order=desc --limit 10 "stars:>1000" --json fullName,description,url'
        result = subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8')

        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return []

        try:
            repos_data = json.loads(result.stdout)
            repos = []
            for item in repos_data:
                repos.append({
                    'full_name': item.get('fullName', ''),
                    'description': item.get('description', ''),
                    'url': item.get('url', f"https://github.com/{item.get('fullName', '')}")
                })
            print(f"Found {len(repos)} trending repos")
            return repos
        except Exception as e:
            print(f"Parse error: {e}")
            return []

    def analyze_repo(self, repo_full_name):
        """Phase 2: Analyze repository structure"""
        print(f"\n=== Phase 2: Analyzing {repo_full_name} ===")

        # Get repo info
        result = subprocess.run(
            f'gh repo view {repo_full_name} --json description,stargazerCount,primaryLanguage,issues',
            shell=True, capture_output=True, encoding='utf-8'
        )

        if result.returncode != 0:
            print(f"  Error fetching repo info")
            return None

        try:
            info = json.loads(result.stdout)
            stars = info.get('stargazerCount', 0)
            lang = info.get('primaryLanguage', {})
            lang_name = lang.get('name', 'Unknown') if lang else 'Unknown'
            issues_data = info.get('issues', {})
            issues_count = issues_data.get('totalCount', 0) if isinstance(issues_data, dict) else 0

            print(f"  Stars: {stars:,}")
            print(f"  Language: {lang_name}")
            print(f"  Issues: {issues_count}")

            return {
                'stargazerCount': stars,
                'primaryLanguage': {'name': lang_name},
                'openIssuesCount': issues_count,
                'description': info.get('description', '')
            }
        except Exception as e:
            print(f"  Parse error: {e}")
            return None

    def find_contribution_opportunities(self, repo_full_name):
        """Phase 3: Find contribution opportunities"""
        print(f"\n=== Phase 3: Finding contribution opportunities ===")

        opportunities = []

        # Check for good first issues
        result = subprocess.run(
            f'gh issue list --repo {repo_full_name} --label "good first issue,help wanted,bug" --limit 5 --state open',
            shell=True, capture_output=True, text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        opportunities.append({
                            'type': 'issue',
                            'number': parts[0],
                            'title': parts[2] if len(parts) > 2 else 'Unknown',
                            'url': f"https://github.com/{repo_full_name}/issues/{parts[0]}"
                        })

        # Check for documentation improvements
        result = subprocess.run(
            f'gh issue list --repo {repo_full_name} --search "documentation,docs,typo" --limit 3 --state open',
            shell=True, capture_output=True, text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split('\n')[:3]:
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        opportunities.append({
                            'type': 'docs',
                            'number': parts[0],
                            'title': parts[2],
                            'url': f"https://github.com/{repo_full_name}/issues/{parts[0]}"
                        })

        print(f"Found {len(opportunities)} opportunities")
        return opportunities

    def save_to_memory(self, repo_name, analysis, opportunities):
        """Save findings to database"""
        cursor = self.conn.cursor()

        content = f"""
## GitHub Trending Analysis

### Repository: {repo_name}
- Stars: {analysis.get('stargazerCount', 0)}
- Language: {analysis.get('primaryLanguage', {}).get('name', 'Unknown')}
- Open Issues: {analysis.get('openIssuesCount', 0)}

### Contribution Opportunities
"""
        for opp in opportunities:
            content += f"\n- [{opp['type']}] #{opp['number']}: {opp['title']}\n  URL: {opp['url']}\n"

        cursor.execute('''
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('event', f'Trending: {repo_name}', content, 'github',
              json.dumps(['trending', 'pr-opportunity', repo_name.split('/')[1]]),
              6, datetime.now().isoformat()))

        self.conn.commit()
        print(f"Saved to memory: {repo_name}")

    def run_daily(self):
        """Run daily trending analysis"""
        print("=== GitHub Trending PR Automation - Daily Run ===\n")

        # Discover trending repos
        repos = self.discover_trending(language="python", since="daily")

        if not repos:
            print("No trending repos found")
            return

        # Analyze top 3
        for repo in repos[:3]:
            full_name = repo['full_name']

            # Analyze
            analysis = self.analyze_repo(full_name)
            if not analysis:
                continue

            # Find opportunities
            opportunities = self.find_contribution_opportunities(full_name)

            # Save to memory
            if opportunities:
                self.save_to_memory(full_name, analysis, opportunities)

        print("\n=== Daily run complete ===")
        self.conn.close()

if __name__ == "__main__":
    automation = GitHubTrendingPR()
    automation.run_daily()
