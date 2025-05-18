from playwright.sync_api import sync_playwright, TimeoutError
import os
import requests

def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def login_koyeb(email, password):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        page.goto("https://betadash.lunes.host/login", timeout=60000)

        # 输入邮箱和密码
        page.get_by_placeholder("myemail@gmail.com").fill(email)
        page.get_by_placeholder("Your Password Here").fill(password)

        try:
            # ✅ 等待 Cloudflare iframe 出现
            frame_element = page.wait_for_selector("iframe[src*='challenges.cloudflare.com']", timeout=15000)
            frame = frame_element.content_frame()

            if frame is None:
                return f"账号 {email} 登录失败: 无法切入 Cloudflare iframe"

            # ✅ 点击 iframe 中的验证按钮（用 div 或 span）
            frame.click("div[role='button']", timeout=10000)

        except Exception as e:
            return f"账号 {email} 登录失败: 验证点击失败 ({e})"

        # 提交登录
        page.get_by_role("button", name="Submit").click()

        try:
            error_message = page.wait_for_selector('.MuiAlert-message', timeout=5000)
            if error_message:
                return f"账号 {email} 登录失败: {error_message.inner_text()}"
        except:
            try:
                page.wait_for_url("https://betadash.lunes.host", timeout=5000)
                return f"账号 {email} 登录成功!"
            except:
                return f"账号 {email} 登录失败: 未跳转仪表盘"

        finally:
            browser.close()

if __name__ == "__main__":
    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    for account in accounts:
        email, password = account.split(':')
        status = login_koyeb(email, password)
        login_statuses.append(status)
        print(status)

    if login_statuses:
        message = "WEBHOST登录状态:\n\n" + "\n".join(login_statuses)
        result = send_telegram_message(message)
        print("消息已发送到Telegram:", result)
    else:
        error_message = "没有配置任何账号"
        send_telegram_message(error_message)
        print(error_message)
