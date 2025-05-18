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
        browser = p.firefox.launch(headless=True)  # headless 适配无头环境
        page = browser.new_page()

        try:
            page.goto("https://betadash.lunes.host/login", timeout=60000)

            # 填写邮箱密码
            page.fill("input#email", email)
            page.fill("input#password", password)

            # 等待 Cloudflare Turnstile 验证iframe出现，最多等待15秒
            try:
                frame = page.frame_locator("iframe[src*='challenges.cloudflare.com']").frame()
            except Exception:
                frame = None

            if frame:
                try:
                    checkbox = frame.locator("input[type='checkbox']")
                    checkbox.click(timeout=10000)
                    print("验证复选框点击成功")
                except Exception as e:
                    print(f"登录失败: 验证点击失败 {str(e)}")
                    return f"账号 {email} 登录失败: 验证点击失败"
            else:
                print("未检测到验证iframe，可能不需要验证")

            # 点击登录按钮
            page.click("button[type='submit']")

            # 等待错误消息或跳转
            try:
                error_message = page.wait_for_selector('.MuiAlert-message', timeout=5000)
                if error_message:
                    error_text = error_message.inner_text()
                    return f"账号 {email} 登录失败: {error_text}"
            except TimeoutError:
                # 没有错误，检查是否跳转到主页
                try:
                    page.wait_for_url("https://betadash.lunes.host", timeout=5000)
                    return f"账号 {email} 登录成功!"
                except TimeoutError:
                    return f"账号 {email} 登录失败: 未能跳转到仪表板页面"
        except Exception as e:
            return f"账号 {email} 登录失败: 未知错误 {str(e)}"
        finally:
            browser.close()

if __name__ == "__main__":
    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    for account in accounts:
        try:
            email, password = account.split(':')
        except Exception:
            print(f"账号格式错误: {account}")
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
