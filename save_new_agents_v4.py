import sqlite3
import json
from datetime import datetime

# 新增的14个智能体
new_agents = [
    {
        "id": 180,
        "name": "AI Researcher",
        "category": "ai_research",
        "description": "Expert in AI research, machine learning, and deep learning",
        "emoji": "🧠",
        "color": "#8B5CF6",
        "tools": ["Python", "PyTorch", "TensorFlow", "Jupyter"],
        "vibe": "academic",
        "full_content": "AI Researcher content...",
    },
    {
        "id": 181,
        "name": "ML Engineer",
        "category": "ai_research",
        "description": "Machine learning engineer specializing in model deployment and optimization",
        "emoji": "⚙️",
        "color": "#10B981",
        "tools": ["Python", "Scikit-learn", "TensorFlow", "Docker"],
        "vibe": "practical",
        "full_content": "ML Engineer content...",
    },
    {
        "id": 182,
        "name": "LLM Specialist",
        "category": "ai_research",
        "description": "Large Language Model specialist for fine-tuning and deployment",
        "emoji": "🔤",
        "color": "#F59E0B",
        "tools": ["Python", "PyTorch", "Hugging Face", "Transformers"],
        "vibe": "cutting-edge",
        "full_content": "LLM Specialist content...",
    },
    {
        "id": 183,
        "name": "Data Scientist",
        "category": "data_science",
        "description": "Data scientist specializing in analysis, visualization, and machine learning",
        "emoji": "📊",
        "color": "#3B82F6",
        "tools": ["Python", "Pandas", "Scikit-learn", "Matplotlib"],
        "vibe": "analytical",
        "full_content": "Data Scientist content...",
    },
    {
        "id": 184,
        "name": "Data Engineer",
        "category": "data_science",
        "description": "Data engineer specializing in pipelines, ETL, and data infrastructure",
        "emoji": "🔧",
        "color": "#6366F1",
        "tools": ["Python", "SQL", "Airflow", "Spark"],
        "vibe": "infrastructure",
        "full_content": "Data Engineer content...",
    },
    {
        "id": 185,
        "name": "Security Analyst",
        "category": "security",
        "description": "Security analyst specializing in vulnerability assessment and threat analysis",
        "emoji": "🔒",
        "color": "#EF4444",
        "tools": ["Python", "Burp Suite", "Metasploit", "Wireshark"],
        "vibe": "defensive",
        "full_content": "Security Analyst content...",
    },
    {
        "id": 186,
        "name": "Financial Analyst",
        "category": "finance",
        "description": "Financial analyst specializing in market analysis and investment research",
        "emoji": "💰",
        "color": "#10B981",
        "tools": ["Python", "Excel", "Bloomberg", "Reuters"],
        "vibe": "analytical",
        "full_content": "Financial Analyst content...",
    },
    {
        "id": 187,
        "name": "Healthcare Analyst",
        "category": "healthcare",
        "description": "Healthcare analyst specializing in medical data analysis and healthcare operations",
        "emoji": "🏥",
        "color": "#EC4899",
        "tools": ["Python", "SQL", "Tableau", "HIPAA"],
        "vibe": "care-focused",
        "full_content": "Healthcare Analyst content...",
    },
    {
        "id": 188,
        "name": "Education Specialist",
        "category": "education",
        "description": "Education specialist focusing on curriculum design and learning optimization",
        "emoji": "📚",
        "color": "#8B5CF6",
        "tools": ["Python", "Learning Management Systems", "Analytics", "Content Creation"],
        "vibe": "educational",
        "full_content": "Education Specialist content...",
    },
    {
        "id": 189,
        "name": "Legal Analyst",
        "category": "legal",
        "description": "Legal analyst specializing in contract analysis and legal research",
        "emoji": "⚖️",
        "color": "#6366F1",
        "tools": ["Python", "Legal Research Tools", "Document Analysis", "Compliance"],
        "vibe": "precise",
        "full_content": "Legal Analyst content...",
    },
    {
        "id": 190,
        "name": "Content Strategist",
        "category": "content_creation",
        "description": "Content strategist specializing in content planning and audience engagement",
        "emoji": "✍️",
        "color": "#F59E0B",
        "tools": ["Content Management", "Analytics", "SEO", "Social Media"],
        "vibe": "creative",
        "full_content": "Content Strategist content...",
    },
    {
        "id": 191,
        "name": "Automation Engineer",
        "category": "automation",
        "description": "Automation engineer specializing in workflow automation and process optimization",
        "emoji": "🤖",
        "color": "#10B981",
        "tools": ["Python", "Automation Tools", "API Integration", "Workflow Design"],
        "vibe": "efficient",
        "full_content": "Automation Engineer content...",
    },
    {
        "id": 192,
        "name": "Business Analyst",
        "category": "analysis",
        "description": "Business analyst specializing in business process analysis and requirements gathering",
        "emoji": "📈",
        "color": "#3B82F6",
        "tools": ["Python", "SQL", "Process Modeling", "Requirements Analysis"],
        "vibe": "analytical",
        "full_content": "Business Analyst content...",
    },
    {
        "id": 193,
        "name": "Management Consultant",
        "category": "consulting",
        "description": "Management consultant specializing in strategy and organizational transformation",
        "emoji": "👔",
        "color": "#6366F1",
        "tools": ["Strategic Planning", "Change Management", "Data Analysis", "Presentation"],
        "vibe": "strategic",
        "full_content": "Management Consultant content...",
    },
]

# 保存到数据库
print("Saving new agents to database...")

try:
    conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
    cursor = conn.cursor()

    # 保存每个智能体
    for agent in new_agents:
        try:
            # 生成唯一的filepath
            filepath = f"agents/{agent['category']}/{agent['name'].lower().replace(' ', '_')}.md"
            
            cursor.execute("""
                INSERT OR REPLACE INTO agent_prompts
                (id, name, category, description, emoji, color, tools, vibe, filepath, full_content, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent["id"],
                agent["name"],
                agent["category"],
                agent["description"],
                agent["emoji"],
                agent["color"],
                json.dumps(agent["tools"]),
                agent["vibe"],
                filepath,
                agent["full_content"],
                json.dumps({}),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ))
            print(f"  Saved: {agent['name']} (ID {agent['id']}, filepath: {filepath})")
        except Exception as e:
            print(f"  Error saving {agent['name']}: {e}")

    conn.commit()
    conn.close()

    print(f"\nSuccessfully saved agents to database")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
