from playwright.sync_api import sync_playwright, TimeoutError
import os
import requests
import time

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

        # 定位 Cloudflare 验证方框的复选框元素
        checkbox = page.get_by_role("checkbox", name="Verify you are human")

        # 点击该复选框元素,最多重试 5 次,每次重试间隔 2 秒
        for _ in range(5):
            if checkbox.is_visible() and checkbox.is_enabled():
                try:
                    checkbox.click()
                    break  # 如果点击成功,退出循环
                except TimeoutError:
                    print("点击复选框超时,重试中...")
            else:
                print("复选框元素未就绪,等待 2 秒后重试...")
            time.sleep(2)
        else:
            return f"账号 {email} 登录失败: 无法点击 Cloudflare 验证复选框"

        # 点击登录按钮
        page.get_by_role("button", name="Submit").click()

        # 等待可能出现的错误消息或成功登录后的页面
        try:
            # 等待可能的错误消息
            error_message = page.wait_for_selector('.MuiAlert-message', timeout=5000)
            if error_message:
                error_text = error_message.inner_text()
                return f"账号 {email} 登录失败: {error_text}"
        except:
            # 如果没有找到错误消息,检查是否已经跳转到仪表板页面
            try:
                page.wait_for_url("https://betadash.lunes.host", timeout=5000)
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
        error_message
