import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime

# --- 配置区域 (从GitHub Secrets读取) ---
API_KEY = os.environ["NEWS_API_KEY"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASSWORD"]
TARGET_EMAIL = EMAIL_USER  # 默认发给自己

def get_news():
    # 获取全球(美国)头条，你也可以把 'us' 改成 'cn' (但中文源较少)
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=general&pageSize=10&apiKey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get("articles", [])

def send_email(articles):
    if not articles:
        print("没有获取到新闻！")
        return

    # 获取当前日期
    today = datetime.now().strftime("%Y-%m-%d %A")
    
    # --- 生成 HTML 邮件内容 (Vibe: 纽约时报风格) ---
    html_content = f"""
    <html>
    <body style="font-family: 'Georgia', serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h1 style="color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; font-size: 24px;">
                🌍 Daily Briefing
            </h1>
            <p style="color: #666; font-style: italic;">{today}</p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
    """

    for article in articles:
        title = article.get('title', 'No Title')
        desc = article.get('description') or 'Click to read more...'
        url = article.get('url')
        source = article.get('source', {}).get('name', 'Unknown')
        
        # 过滤掉无效新闻
        if title == "[Removed]": continue

        html_content += f"""
            <div style="margin-bottom: 25px;">
                <h3 style="margin: 0 0 5px 0; font-size: 18px;">
                    <a href="{url}" style="color: #2c3e50; text-decoration: none;">{title}</a>
                </h3>
                <span style="background-color: #eee; color: #555; padding: 2px 6px; font-size: 12px; border-radius: 4px;">{source}</span>
                <p style="color: #555; line-height: 1.6; font-size: 14px; margin-top: 8px;">{desc}</p>
            </div>
        """

    html_content += """
            <div style="margin-top: 30px; text-align: center; color: #999; font-size: 12px;">
                Powered by Vibe Coding | NewsAPI
            </div>
        </div>
    </body>
    </html>
    """

    # --- 发送邮件逻辑 ---
    msg = MIMEText(html_content, 'html', 'utf-8')
    msg['From'] = Header("Daily News Bot", 'utf-8')
    msg['To'] = TARGET_EMAIL
    msg['Subject'] = Header(f"早安新闻: {today}", 'utf-8')

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [TARGET_EMAIL], msg.as_string())
        server.quit()
        print("✅ 邮件发送成功！")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    articles = get_news()
    send_email(articles)
