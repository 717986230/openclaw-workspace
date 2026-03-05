#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Monitor - 检查新邮件并自动回复
"""

import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header, decode_header
from datetime import datetime, timedelta
import email.utils
import os

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'email_config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

EMAIL_CONFIG = config['email']
MONITOR_CONFIG = config['monitor']

# 关键词
KEYWORDS = MONITOR_CONFIG['keywords']
IGNORE_KEYWORDS = MONITOR_CONFIG.get('ignoreKeywords', [])
IGNORE_SENDERS = MONITOR_CONFIG.get('ignoreSenders', [])
IGNORE_TIME = MONITOR_CONFIG.get('ignoreTime', '08:00')
DELETE_SPAM = MONITOR_CONFIG.get('deleteSpam', True)

# 自动回复模板（中英双语）
REPLY_TEMPLATE = """\
【中文】
您好！感谢联系 OpenClaw 技能开发服务。

【服务内容】
- OpenClaw 技能定制开发：5000-20000 元/个
- AI 自动化系统集成：10000-50000 元/项目
- 企业培训/技术咨询：20000 元/场

【已发布技能】
- Weekly Digest（AI 周报生成器）：https://clawhub.ai/sukimgit/weekly-digest
- Email Monitor（邮件自动监控）：https://clawhub.ai/sukimgit/email-monitor

【案例展示】
- AI 视觉监控系统：小区物业火灾监控，3.98W/套
- 自动化获客系统：GitHub/Twitter 监控 + 自动回复
- 多 Agent 协作系统：同时指挥 10 个 AI 并行工作

【联系方式】
📧 邮箱：1776480440@qq.com
💬 微信：私信获取

如有具体需求，欢迎详细沟通！

---

【English】
Hello! Thank you for contacting OpenClaw skill development services.

【Services】
- Custom Skill Development: $700-3000 USD
- AI Automation Integration: $1500-7000 USD
- Enterprise Training: $3000/session

【Published Skills】
- Weekly Digest: https://clawhub.ai/sukimgit/weekly-digest
- Email Monitor: https://clawhub.ai/sukimgit/email-monitor

【Contact】
📧 Email: 1776480440@qq.com
💬 WeChat: DM for details

【Payment 支付方式】
- Domestic (China) 国内：WeChat Pay / Alipay / Bank Transfer
- International 国际：
  - PayPal: https://paypal.me/monet888 (账号：1776480440@qq.com)
  - Wise: 
    - Account: 242009405
    - BSB: 774-001 (AU only)
    - SWIFT: TRWIAUS1XXX (International)
    - Bank: Wise Australia Pty Ltd
  - USDT (Crypto): 私信获取 DM for details

Please share your requirements, I'll provide a detailed quote.
欢迎告诉我您的具体需求，我会给您详细报价！

Best regards,
老高 | OpenClaw Team
"""


def decode_mime(word):
    """解码 MIME 编码的邮件头"""
    if not word:
        return ""
    decoded = decode_header(word)
    text = ""
    for content, encoding in decoded:
        if isinstance(content, bytes):
            text += content.decode(encoding or 'utf-8', errors='ignore')
        else:
            text += content
    return text


def should_ignore_email(from_email, subject, body, email_date):
    """判断是否应该忽略邮件"""
    text_to_check = (from_email + " " + subject + " " + body).lower()
    
    # 检查忽略关键词
    for keyword in IGNORE_KEYWORDS:
        if keyword.lower() in text_to_check:
            return True, f"包含忽略关键词：{keyword}"
    
    # 检查忽略发件人
    for sender in IGNORE_SENDERS:
        if sender.lower() in from_email.lower():
            return True, f"忽略发件人：{sender}"
    
    # 检查是否是早 8 点的服务器维护邮件
    if IGNORE_TIME:
        try:
            # 解析邮件时间
            email_time = email.utils.parsedate_to_datetime(email_date)
            if email_time.hour == 8 and "服务器" in text_to_check or "维护" in text_to_check:
                return True, "早 8 点服务器维护邮件"
        except:
            pass
    
    return False, ""


def is_spam(subject, body):
    """判断是否是垃圾邮件"""
    spam_indicators = ["发票", "代开", "赌博", "彩票", "贷款", "办证", "sex", "porn"]
    text_to_check = (subject + " " + body).lower()
    
    for indicator in spam_indicators:
        if indicator.lower() in text_to_check:
            return True
    
    return False


def check_emails():
    """检查新邮件"""
    print(f"[{datetime.now()}] 开始检查邮件...")
    
    # 连接 IMAP
    print(f"连接到 {EMAIL_CONFIG['imap']['host']}:{EMAIL_CONFIG['imap']['port']}")
    mail = imaplib.IMAP4_SSL(EMAIL_CONFIG['imap']['host'], EMAIL_CONFIG['imap']['port'])
    print("登录中...")
    mail.login(EMAIL_CONFIG['imap']['auth']['user'], EMAIL_CONFIG['imap']['auth']['pass'])
    print("登录成功！")
    
    # 选择收件箱（163 邮箱用空字符串选择默认）
    print("选择收件箱...")
    status, messages = mail.select()  # 空字符串选择默认文件夹
    if status != 'OK':
        print(f"选择收件箱失败：{status}")
        # 尝试 INBOX
        status, messages = mail.select('INBOX')
        if status != 'OK':
            print(f"尝试 INBOX 也失败：{status}")
            return []
    print("收件箱选择成功！")
    
    # 搜索过去 1 小时的未读邮件
    since_date = (datetime.now() - timedelta(hours=1)).strftime('%d-%b-%Y')
    print(f"搜索 {since_date} 之后的未读邮件...")
    status, messages = mail.search(None, f'(SINCE "{since_date}" UNSEEN)')
    
    if status != 'OK':
        print("没有新邮件")
        return []
    
    email_ids = messages[0].split()
    print(f"找到 {len(email_ids)} 封新邮件")
    
    business_emails = []
    
    for email_id in email_ids:
        # 获取邮件内容
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        if status != 'OK':
            continue
        
        # 解析邮件
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # 获取发件人
        from_ = decode_mime(msg.get('From', ''))
        subject = decode_mime(msg.get('Subject', ''))
        date = msg.get('Date', '')
        
        # 获取邮件正文
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors='ignore')
            except:
                pass
        
        # 检查是否应该忽略
        should_ignore, ignore_reason = should_ignore_email(from_, subject, body, date)
        if should_ignore:
            print(f"  [忽略] {subject[:50]} - {ignore_reason}")
            # 标记为已读
            mail.store(email_id, '+FLAGS', '\\Seen')
            continue
        
        # 检查是否是垃圾邮件
        if DELETE_SPAM and is_spam(subject, body):
            print(f"  [垃圾] {subject[:50]} - 删除中...")
            # 移动到垃圾箱
            mail.copy(email_id, 'Spam')
            mail.store(email_id, '+FLAGS', '\\Deleted')
            continue
        
        # 检查关键词
        text_to_check = (subject + " " + body).lower()
        matched_keywords = [kw for kw in KEYWORDS if kw.lower() in text_to_check]
        
        if matched_keywords:
            print(f"[商机] 发现商机邮件！关键词：{matched_keywords}")
            print(f"  发件人：{from_}")
            print(f"  主题：{subject}")
            
            business_emails.append({
                'id': email_id,
                'from': from_,
                'subject': subject,
                'date': date,
                'body': body[:200],  # 前 200 字
                'keywords': matched_keywords
            })
            
            # 标记为已读
            mail.store(email_id, '+FLAGS', '\\Seen')
        else:
            print(f"  [普通] {subject[:50]}")
    
    mail.close()
    mail.logout()
    
    return business_emails


def send_reply(to_email, original_subject):
    """发送自动回复"""
    print(f"发送自动回复到：{to_email}")
    
    # 回复主题
    if not original_subject.lower().startswith('re:'):
        reply_subject = f"Re: {original_subject}"
    else:
        reply_subject = original_subject
    
    # 创建邮件（修复 From 头格式）
    from email.mime.multipart import MIMEMultipart
    from email.header import Header
    
    msg = MIMEMultipart()
    msg.attach(MIMEText(REPLY_TEMPLATE, 'plain', 'utf-8'))
    msg['From'] = EMAIL_CONFIG['address']  # 只用邮箱地址
    msg['To'] = to_email
    msg['Subject'] = Header(reply_subject, 'utf-8')
    
    try:
        # 连接 SMTP 并发送
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp']['host'], EMAIL_CONFIG['smtp']['port'])
        server.login(EMAIL_CONFIG['smtp']['auth']['user'], EMAIL_CONFIG['smtp']['auth']['pass'])
        server.send_message(msg)
        server.quit()
        print("[OK] 回复发送成功")
        return True
    except Exception as e:
        print(f"[FAIL] 回复发送失败：{e}")
        return False


def send_feishu_notification(business_emails):
    """发送飞书通知"""
    # TODO: 调用飞书 API 发送通知
    print(f"[飞书] 通知：发现 {len(business_emails)} 封商机邮件")
    for em in business_emails:
        print(f"  - {em['from']}: {em['subject']}")


def main():
    """主函数"""
    print("=" * 60)
    print("Email Monitor - 邮件自动监控")
    print("=" * 60)
    
    # 检查新邮件
    business_emails = check_emails()
    
    if business_emails:
        print(f"\n[统计] 发现 {len(business_emails)} 封商机邮件")
        
        # 自动回复
        if MONITOR_CONFIG.get('autoReply', True):
            for em in business_emails:
                # 提取邮箱地址（简单处理）
                from_email = em['from'].split('<')[-1].strip('>') if '<' in em['from'] else em['from']
                send_reply(from_email, em['subject'])
        
        # 飞书通知
        if MONITOR_CONFIG.get('notifyFeishu', True):
            send_feishu_notification(business_emails)
    else:
        print("\n[统计] 没有发现商机邮件")
    
    print("\n检查完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
