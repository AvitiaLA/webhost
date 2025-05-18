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

        try:
            page.goto("https://betadash.lunes.host/login", timeout=60000)

            # 填写邮箱和密码
            page.fill('input[placeholder="myemail@gmail.com"]', email)
            page.fill('input[placeholder="Your Password Here"]', password)

            # 尝试点击Cloudflare验证复选框（如果存在）
            try:
                checkbox = page.locator("input[type='checkbox']")
                if checkbox.is_visible():
                    checkbox.click()
            except Exception:
                # 如果不存在或点击失败，忽略
                pass

            # 点击登录按钮
            page.click('button:has-text("Submit")')

            # 等待错误消息或判断跳转
            try:
                error_message = page.wait_for_selector('.MuiAlert-message', timeout=5000)
                if error_message:
                    error_text = error_message.inner_text()
                    return f"账号 {email} 登录失败: {error_text}"
            except TimeoutError:
                # 没有错误消息，改成判断URL是否仍在登录页
                current_url = page.url
                if "/login" not in current_url:
                    return f"账号 {email} 登录成功!"
                else:
                    return f"账号 {email} 登录失败: 未能跳转到仪表板页面"
        finally:
            browser.close()

if __name__ == "__main__":
    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    for account in accounts:
        try:
            email, password = account.split(':')
        except ValueError:
            print(f"账号格式错误，跳过：{account}")
            continue

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
