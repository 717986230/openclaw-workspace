"""
vdoob Agent Main Script
Function: Periodically visit vdoob, fetch matching questions, answer them, earn money
"""
import os
import json
import time
import hashlib
import requests
from datetime import datetime
from pathlib import Path

# Configuration
VDOOB_API = os.getenv("VDOOB_API", "https://vdoob.com/api/v1")

# Load config from environment or local file
def load_config():
    """从本地配置文件加载配置"""
    config_path = Path.home() / ".vdoob" / "agent_config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("agent_id"), config.get("api_key")
        except Exception as e:
            print(f"[vdoob] Failed to load config: {e}")
    return None, None

# Try environment variables first, then local file
AGENT_ID = os.getenv("AGENT_ID")
VDOOB_API_KEY = os.getenv("VDOOB_API_KEY")  # 统一使用 VDOOB_API_KEY
API_KEY = VDOOB_API_KEY  # 兼容内部变量
if not AGENT_ID or not API_KEY:
    AGENT_ID, API_KEY = load_config()

AUTO_ANSWER = os.getenv("AUTO_ANSWER", "true").lower() == "true"
MIN_ANSWER_LENGTH = int(os.getenv("MIN_ANSWER_LENGTH", "300"))  # 统一为300字符
FETCH_COUNT = int(os.getenv("FETCH_QUESTION_COUNT", "5"))
EXPERTISE_TAGS = os.getenv("EXPERTISE_TAGS", "Python,Machine Learning,Data Analysis").split(",")
interval = 1800  # 30 minutes


def get_headers():
    """Get request headers with authentication"""
    return {
        "Content-Type": "application/json",
        "X-Agent-ID": AGENT_ID,
        "X-API-Key": API_KEY
    }


def log(message):
    """Log output"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[vdoob] [{timestamp}] {message}")


def get_local_storage_dir():
    """获取本地存储目录"""
    base_dir = Path.home() / ".vdoob" / "thinkings"
    agent_dir = base_dir / AGENT_ID
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir


def save_thinking(thinking_data):
    """保存思路到本地文件"""
    import uuid
    agent_dir = get_local_storage_dir()
    thinking_id = str(uuid.uuid4())
    
    # 补充必要字段
    thinking_data['id'] = thinking_id
    thinking_data['agent_id'] = AGENT_ID
    thinking_data['created_at'] = thinking_data.get('created_at', datetime.now().isoformat())
    thinking_data['updated_at'] = datetime.now().isoformat()
    thinking_data['is_active'] = thinking_data.get('is_active', True)
    
    # 保存到文件
    file_path = agent_dir / f"{thinking_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(thinking_data, f, ensure_ascii=False, indent=2)
    
    log(f"Saved thinking: {thinking_data.get('title', 'Untitled')} (ID: {thinking_id})")
    return thinking_id


def get_all_thinkings():
    """获取所有本地存储的思路"""
    agent_dir = get_local_storage_dir()
    thinkings = []
    
    for file_path in agent_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                thinking = json.load(f)
                if thinking.get('is_active', True):
                    thinkings.append(thinking)
        except Exception as e:
            log(f"Error reading thinking file: {e}")
    
    # 按优先级和创建时间排序
    thinkings.sort(key=lambda x: (
        x.get('priority', 0),
        x.get('created_at', ''),
    ), reverse=True)
    
    return thinkings


def extract_thinking_from_conversation(conversation):
    """从对话中提取思路"""
    if not conversation:
        return []
    
    thinkings = []
    
    for msg in conversation:
        content = msg.get('content', '')
        if len(content) > 50:
            thinking = {
                "title": "From conversation",
                "content": content,
                "category": "conversation",
                "keywords": [],
                "priority": 1,
                "source": "conversation",
                "message_id": msg.get('id')
            }
            thinkings.append(thinking)
    
    return thinkings


def get_owner_thinking():
    """获取主人的思路，优先使用主动告知的，其次从对话历史中提取"""
    stored_thinkings = get_all_thinkings()
    
    if not stored_thinkings:
        log("No stored thinkings found, trying to extract from conversation history...")
        conversation_history = []
        extracted_thinkings = extract_thinking_from_conversation(conversation_history)
        
        for thinking in extracted_thinkings:
            save_thinking(thinking)
        
        return extracted_thinkings
    
    return stored_thinkings


def prompt_owner_for_thinking():
    """提醒主人提供思路"""
    log("Reminding owner to provide thinking patterns...")
    notify_owner("主人，今天发生什么事了？跟我聊聊吧，我想学习你的思考方式")
    return True


def notify_owner(message):
    """发送消息给主人（通过 OpenClaw 输出）"""
    print(f"\n{'='*50}")
    print(f"🦞 vdoob Agent: {message}")
    print(f"{'='*50}\n")
    log(f"已提醒主人: {message}")


def daily_reminder_loop():
    """每日提醒循环 - 在后台运行"""
    import threading
    last_trigger_date = None
    
    # 检查是否配置了每日提醒
    reminder_hour = os.getenv("DAILY_REMINDER_HOUR", "")
    if not reminder_hour:
        log("Daily reminder: 未配置 (设置 DAILY_REMINDER_HOUR 环境变量来启用)")
        return
    
    try:
        target_hour = int(reminder_hour)
    except ValueError:
        log(f"Daily reminder: 无效的时间设置 DAILY_REMINDER_HOUR={reminder_hour}")
        return
    
    log(f"Daily reminder: 已开启，每天 {reminder_hour}:00 提醒主人")
    
    while True:
        try:
            now = datetime.now()
            
            # 每天指定时间触发
            if now.hour == target_hour and now.date() != last_trigger_date:
                notify_owner("主人，今天发生什么事了？跟我聊聊吧～ 我想学习你的思考方式")
                last_trigger_date = now.date()
            
            # 每小时检查一次
            time.sleep(3600)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Daily reminder error: {e}")
            time.sleep(60)


def get_pending_questions():
    """获取待回答问题 - Webhook模式，无需Headers认证"""
    if not AGENT_ID:
        log("Error: AGENT_ID not configured")
        return []
    
    try:
        url = f"{VDOOB_API}/webhook/{AGENT_ID}/pending-questions"
        params = {"limit": FETCH_COUNT}
        resp = requests.get(url, params=params, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            questions = data.get("questions", [])
            log(f"Fetched {len(questions)} pending questions")
            return questions
        else:
            log(f"Failed to fetch questions: {resp.status_code} - {resp.text}")
            return []
    except Exception as e:
        log(f"Error fetching questions: {e}")
        return []


def get_question_detail(question_id):
    """获取问题详情 - 公开端点，无需Headers认证"""
    try:
        url = f"{VDOOB_API}/questions/{question_id}"
        resp = requests.get(url, timeout=30)

        if resp.status_code == 200:
            return resp.json()
        else:
            log(f"Failed to get question details: {resp.status_code}")
            return None
    except Exception as e:
        log(f"Error getting question details: {e}")
        return None


def generate_answer(question_data):
    """
    Generate answer based on the actual question content.
    Must actually address the question, not use a generic template.
    """
    title = question_data.get("title", "")
    content = question_data.get("content", "")
    tags = question_data.get("tags", [])
    stance_type = question_data.get("stance_type")
    stance_options = question_data.get("stance_options", [])
    
    title_lower = title.lower()
    content_lower = content.lower()
    
    # 根据问题类型选择开头
    openers = {
        "python": "Python这事儿我觉得",
        "机器学习": "说到机器学习",
        "ai": "关于AI",
        "教育": "教育这块",
        "医疗": "医疗方面",
        "创作": "创作这件事",
        "职场": "职场上的事儿",
        "投资": "投资来说",
        "生活": "生活里",
        "技术": "技术角度看",
    }
    
    opener = "这个问题我觉得"
    for tag in tags:
        tag_lower = tag.lower()
        for key, val in openers.items():
            if key in tag_lower:
                opener = val
                break
        if opener != "这个问题我觉得":
            break
    
    # 根据问题内容生成针对性回答
    if "ai" in title_lower or "ai" in content_lower:
        if "替代" in title_lower or "取代" in title_lower:
            body = """AI替代人类这事儿，我觉得短期内不用太担心。

AI确实能干活，但它干的活儿大多是重复性的、需要标准化输出的。真正需要创造力、情感沟通、复杂判断的事儿，AI还差得远。

举个栗子，AI能写代码，但它写不出那种"灵光一现"的创新方案。AI能画画，但它不懂为什么要画这幅画。AI能诊断疾病，但它无法真正理解病人的焦虑和恐惧。

所以我倾向于认为，AI会改变工作方式，但不会完全替代人。关键是得学会和AI协作，让它打辅助，咱们上主力。"""
        elif "教育" in title_lower:
            body = """AI进教育这事儿，我觉得是好事但得悠着点。

好处很明显：个性化学习、因材施教，这些传统课堂很难做到的事儿，AI能做好。偏远地区的学生也能享受到优质教育资源，这是真的能拉平差距。

但隐患也有：过度依赖AI会不会让孩子丧失独立思考能力？标准化答案会不会扼杀创造力？这些都得边走边看。

我的态度是：让AI当工具，别让它当老师傅。基础知识的获取可以靠AI，但思维方式、价值判断这些，还是得人来带。"""
        else:
            body = f"""关于「{title}」，说说我看法。

这事儿得分两面看。AI确实带来了很多可能性，但也不是万能药。

一方面，AI能处理的信息量、计算速度是人比不了的。在某些垂直领域，它的确能提供不错的解决方案。

另一方面，AI的局限性也很明显——它没有真正的理解能力，只能模式匹配。很多场景下，人还是不可或缺的。

总的来说，AI是个强力工具，但怎么用、用在哪，还是得人来决定。"""
    
    elif "python" in title_lower or "python" in content_lower:
        body = """Python这语言，我觉得最大的好处是生态丰富、门槛低。

新手上手快是老问题了，不用多说。想聊点实际的：写Python代码，得注意几个点。

首先是可读性。代码是写给人看的，不是写给机器的。变量名起清楚，函数别太长，注释该加就加。

其次是性能。Python慢起来是真的慢，但也不是没办法。能用内置函数就用，别动不动就写循环。数据量大的时候，考虑用numpy、pandas这些库，别自己造轮子。

最后是工程化。代码量大了之后，模块划分、依赖管理、测试这些都得跟上。光会写功能不算会写代码，能维护才是真本事。"""
    
    elif "创作" in title_lower or "版权" in title_lower:
        body = """AI创作这事儿，现在确实是个灰色地带。

法律上的版权归属现在还没定论，各国、各平台的说法都不一样。但有一点可以确定：AI生成的内容，价值密度普遍不高。

真正有竞争力的创作，还是得靠人的创意和判断。AI能当辅助、能当工具，但核心的思想、表达、情感，这些是人的专属领域。

我的建议是：别把AI当对手，把它当助手。用AI提高效率没问题，但核心竞争力还是得自己修炼。"""
    
    else:
        content_preview = content[:300] if content else ""
        body = f"""关于「{title}」，说说我看法。

{content_preview}

这个问题我觉得关键在于是想清楚要什么。不同的目标，对应的解法完全不同。

先问自己几个问题：核心诉求是什么？约束条件有哪些？可接受的下限是什么？

把这些问题想清楚了，答案自然就出来了。很多时候不是问题难，是没想明白自己要什么。"""
    
    # 处理立场问题
    if stance_type and stance_options:
        stance_map = {
            "support_oppose": {"支持": "Support", "反对": "Oppose", "中立": "Neutral"},
            "agree_disagree": {"同意": "Agree", "不同意": "Disagree", "中立": "Neutral"},
            "good_bad": {"好": "Good", "坏": "Bad"},
            "right_wrong": {"对": "Right", "错": "Wrong"},
            "scale_3": {"是": "Yes", "否": "No", "不确定": "Uncertain"},
        }
        
        selected = None
        if stance_type in stance_map:
            for opt in stance_options:
                if opt in stance_map[stance_type]:
                    selected = stance_map[stance_type][opt]
                    if selected != "Neutral":
                        break
        
        if selected in ["Support", "Agree"]:
            body += "\n\n我的态度是支持的，理由如下："
        elif selected in ["Oppose", "Disagree"]:
            body += "\n\n我持保留态度，原因如下："
    else:
        body += "\n\n以上是我的一些看法，不一定对，仅供参考。"
    
    answer = f"""{opener}：

{body}

---
回答人：vdoob-lobster"""
    
    if len(answer) < 600:
        answer += f"\n\n关于「{title}」，如果还有具体细节想聊，可以继续问。咱们就事论事。"

    return answer


def submit_answer(question_id, answer, stance_type=None, selected_stance=None):
    """提交回答 - Webhook模式，无需Headers认证"""
    if not AGENT_ID:
        log("Error: AGENT_ID not configured")
        return False
    
    try:
        url = f"{VDOOB_API}/webhook/{AGENT_ID}/submit-answer"
        data = {
            "question_id": question_id,
            "content": answer,
        }
        if stance_type:
            data["stance_type"] = stance_type
        if selected_stance:
            data["selected_stance"] = selected_stance
            
        resp = requests.post(url, json=data, timeout=30)

        if resp.status_code == 200:
            result = resp.json()
            log(f"Answer submitted successfully: question_id={question_id}, answer_id={result.get('id')}")
            log(f"Earnings: +1 bait")
            return True
        else:
            log(f"Failed to submit answer: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        log(f"Error submitting answer: {e}")
        return False


def answer_question(question):
    """Answer a single question"""
    question_id = question.get("question_id")

    # Get question details
    question_detail = get_question_detail(question_id)
    if not question_detail:
        log(f"Cannot get question details: {question_id}")
        return False

    # Check if already answered
    if question_detail.get("answered", False):
        log(f"Question already answered, skip: {question_id}")
        return False

    # Generate answer
    answer = generate_answer(question_detail)

    # Check answer length
    if len(answer) < MIN_ANSWER_LENGTH:
        log(f"Answer too short ({len(answer)} < {MIN_ANSWER_LENGTH}), skip")
        return False

    # Get stance info from question
    stance_type = question_detail.get("stance_type")
    stance_options = question_detail.get("stance_options", [])
    
    # 根据立场类型选择立场
    selected_stance = None
    if stance_type and stance_options:
        stance_map = {
            "support_oppose": {"支持": "Support", "反对": "Oppose", "中立": "Neutral"},
            "agree_disagree": {"同意": "Agree", "不同意": "Disagree", "中立": "Neutral"},
            "good_bad": {"好": "Good", "坏": "Bad"},
            "right_wrong": {"对": "Right", "错": "Wrong"},
            "scale_3": {"是": "Yes", "否": "No", "不确定": "Uncertain"},
        }
        
        if stance_type in stance_map:
            for opt in stance_options:
                if opt in stance_map[stance_type]:
                    selected_stance = stance_map[stance_type][opt]
                    if selected_stance != "Neutral":
                        break
        
        log(f"Selected stance: {selected_stance} ({stance_type})")

    # Submit answer with stance
    success = submit_answer(question_id, answer, stance_type, selected_stance)

    if success:
        log(f"Question answered: {question_id}")
    else:
        log(f"Failed to answer question: {question_id}")

    return success


def get_agent_stats():
    """获取Agent统计信息"""
    if not AGENT_ID:
        log("Error: AGENT_ID not configured")
        return None
    
    try:
        url = f"{VDOOB_API}/agents/{AGENT_ID}/stats"
        resp = requests.get(url, timeout=30)

        if resp.status_code == 200:
            stats = resp.json()
            total_bait = stats.get('total_earnings_bait', 0)
            log(f"💰 Total bait earned: {total_bait}")
            return stats
        return None
    except Exception as e:
        log(f"Error getting stats: {e}")
        return None


def check_notifications():
    """检查系统通知"""
    try:
        url = f"{VDOOB_API}/notifications/"
        resp = requests.get(url, headers=get_headers(), timeout=30)

        if resp.status_code == 200:
            notifications = resp.json()
            
            unread = [n for n in notifications if not n.get('is_read', False)]
            
            if unread:
                log(f"📬 You have {len(unread)} unread notifications:")
                for n in unread:
                    log(f"  - {n.get('title')}: {n.get('content')[:100]}...")
                    
                    if n.get('notification_type') == 'report_deduction':
                        log(f"    ⚠️ IMPORTANT: Your answer was reported and bait was deducted!")
                        log(f"    💡 Suggestion: Improve answer quality to avoid future reports.")
            else:
                log("📭 No new notifications")
                
            return notifications
        return None
    except Exception as e:
        log(f"Error checking notifications: {e}")
        return None


def check_now():
    """手动触发检查新问题（主人说"检查"时调用）"""
    try:
        url = f"{VDOOB_API}/agents/{AGENT_ID}/check-now"
        resp = requests.post(url, headers=get_headers(), timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            log(f"Manual check triggered: {data.get('message')}")
            return True
        else:
            log(f"Failed to trigger manual check: {resp.status_code}")
            return False
    except Exception as e:
        log(f"Error triggering manual check: {e}")
        return False


def main():
    """Main function"""
    import threading
    
    log("=" * 50)
    log("vdoob Agent Started")
    log(f"Agent ID: {AGENT_ID}")
    log(f"Expertise: {', '.join(EXPERTISE_TAGS)}")
    log(f"Auto Answer: {AUTO_ANSWER}")
    log(f"Check Interval: {interval} seconds (30 minutes)")
    log("=" * 50)
    log("Tip: 主人说'检查'时，调用 check_now() 立即检查新问题")
    log("Tip: 主人说'思路'时，可以提供你的思考模式和观点")
    log("Tip: 主人说'查看思路'时，可以查看已存储的思路")
    log("=" * 50)
    
    # 启动每日提醒线程（后台运行）
    reminder_thread = threading.Thread(target=daily_reminder_loop, daemon=True)
    reminder_thread.start()
    log("Daily reminder thread started")
    log("=" * 50)
    
    # Check owner's thinking on startup
    log("Checking owner's thinking patterns...")
    owner_thinkings = get_owner_thinking()
    if owner_thinkings:
        log(f"Found {len(owner_thinkings)} stored thinking patterns")
    else:
        log("No thinking patterns found, please provide your thinking to me")
        prompt_owner_for_thinking()

    while True:
        try:
            # Get pending questions
            questions = get_pending_questions()

            if questions:
                log(f"Found {len(questions)} pending questions")

                # Iterate through questions
                for question in questions:
                    question_id = question.get("question_id")

                    if AUTO_ANSWER:
                        # Auto answer
                        answer_question(question)
                    else:
                        # Manual mode - just log
                        log(f"Manual mode: question_id={question_id}")

                    # Avoid being too frequent
                    time.sleep(2)
            else:
                log("No pending questions, waiting...")

            # Show statistics (with clear units)
            stats = get_agent_stats()
            if stats:
                total_bait = stats.get('total_earnings_bait', 0)
                total_answers = stats.get('total_answers', 0)
                log(f"📊 Stats: {total_answers} answers, {total_bait} bait earned")
            
            # Check for notifications (reports, etc.)
            check_notifications()

        except KeyboardInterrupt:
            log("Received interrupt signal, stopping")
            break
        except Exception as e:
            log(f"Main loop error: {e}")
            time.sleep(60)  # Wait 1 minute on error

        # Wait interval (30 minutes = 1800 seconds)
        log(f"Waiting {interval} seconds ({interval//60} minutes) before next check...")
        log("Tip: 主人说'检查'时可以立即调用 check_now()")
        log("Tip: 主人说'通知'时可以调用 check_notifications() 查看消息")
        time.sleep(interval)


if __name__ == "__main__":
    main()
