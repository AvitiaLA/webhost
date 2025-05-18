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
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def login_koyeb(email, password):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto("https://betadash.lunes.host/login", timeout=60000)

            page.fill("input#email", email)
            page.fill("input#password", password)

            # 直接点击按钮（无需复选框处理）
            page.click("button[type='submit']")

            # 检查是否跳转成功
            try:
                page.wait_for_url("**/dashboard", timeout=10000)
                result = f"账号 {email} 登录成功!"
            except TimeoutError:
                try:
                    error = page.locator(".MuiAlert-message").text_content()
                    result = f"账号 {email} 登录失败: {error}"
                except:
                    result = f"账号 {email} 登录失败: 未知错误"
        except Exception as e:
            result = f"账号 {email} 登录异常: {e}"
        finally:
            browser.close()
        return result

if __name__ == "__main__":
    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    for account in accounts:
        if ':' not in account:
            continue
        email, password = account.split(':', 1)
        status = login_koyeb(email.strip(), password.strip())
        login_statuses.append(status)
        print(status)

    if login_statuses:
        message = "🔐 WEBHOST 登录状态:\n\n" + "\n".join(login_statuses)
    else:
        message = "❌ 未配置任何账号"

    result = send_telegram_message(message)
    print("消息发送结果:", result)
