from playwright.sync_api import sync_playwright, TimeoutError
import os
import requests

def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not bot_token or not chat_id:
        print("未设置 Telegram 配置")
        return {"ok": False, "description": "Missing token or chat_id"}
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

        page.fill("input#email", email)
        page.fill("input#password", password)

        try:
            frame_element = page.wait_for_selector("iframe[src*='challenges.cloudflare.com']", timeout=15000)
            frame = frame_element.content_frame()
            checkbox = frame.wait_for_selector("input[type='checkbox']", timeout=15000)
            checkbox.click()
        except TimeoutError:
            browser.close()
            return f"账号 {email} 登录失败: 验证复选框点击失败"

        page.click("button[type=submit]")

        try:
            page.wait_for_url("https://betadash.lunes.host", timeout=15000)
        except TimeoutError:
            browser.close()
            return f"账号 {email} 登录失败: 未能跳转到仪表板页面"

        browser.close()
        return f"账号 {email} 登录成功!"

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
