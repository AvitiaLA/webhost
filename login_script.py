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

        # 访问登录页面
        page.goto("https://betadash.lunes.host/login", timeout=60000)

        # 输入邮箱和密码
        page.get_by_placeholder("myemail@gmail.com").click()
        page.get_by_placeholder("myemail@gmail.com").fill(email)
        page.get_by_placeholder("Your Password Here").click()
        page.get_by_placeholder("Your Password Here").fill(password)

        # 替换成等待并点击复选框
        try:
            page.wait_for_selector("input[type='checkbox']", timeout=15000)
            page.locator("input[type='checkbox']").click()
        except Exception as e:
            browser.close()
            return f"账号 {email} 登录失败: 验证复选框点击失败 ({str(e)})"

        # 点击登录按钮
        page.get_by_role("button", name="Submit").click()

        # 等待错误消息或跳转
        try:
            error_message = page.wait_for_selector('.MuiAlert-message', timeout=5000)
            if error_message:
                error_text = error_message.inner_text()
                browser.close()
                return f"账号 {email} 登录失败: {error_text}"
        except:
            try:
                page.wait_for_url("https://betadash.lunes.host", timeout=5000)
                browser.close()
                return f"账号 {email} 登录成功!"
            except:
                browser.close()
                return f"账号 {email} 登录失败: 未能跳转到仪表板页面"

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
