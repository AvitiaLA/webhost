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
        context = browser.new_context()
        page = context.new_page()

        try:
            # 访问登录页面
            page.goto("https://betadash.lunes.host/login", timeout=60000)

            # 输入邮箱和密码
            page.get_by_placeholder("myemail@gmail.com").fill(email)
            page.get_by_placeholder("Your Password Here").fill(password)

        try:
            # 等待复选框出现
            page.wait_for_selector("input[type='checkbox']", timeout=15000)
            # 点击复选框
            page.locator("input[type='checkbox']").click()
            except Exception as e:
            return f"账号 {email} 登录失败: 验证复选框点击失败 ({str(e)})"
            else:
            return f"账号 {email} 登录失败: 无法点击 Cloudflare 验证复选框"

            # 点击登录按钮
            page.get_by_role("button", name="Submit").click()

            # 检查是否有错误消息
            try:
                error_message = page.wait_for_selector('.MuiAlert-message', timeout=5000)
                if error_message:
                    error_text = error_message.inner_text()
                    return f"账号 {email} 登录失败: {error_text}"
            except:
                # 如果没有错误消息，检查是否跳转成功
            try:
                    page.wait_for_url("https://betadash.lunes.host", timeout=15000)
                    return f"账号 {email} 登录成功!"
                except:
                    return f"账号 {email} 登录失败: 未能跳转到仪表板页面"
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
