import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")
LOGIN_URL = "https://betadash.lunes.host/login"
SUCCESS_URL = "https://betadash.lunes.host"  # 登录成功跳转的URL

def login():
    if not EMAIL or not PASSWORD:
        print("未设置登录凭据，请在环境变量中设置 LOGIN_EMAIL 和 LOGIN_PASSWORD")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York"
        )
        page = context.new_page()

        try:
            print("访问登录页面...")
            page.goto(LOGIN_URL, timeout=60000)

            print("等待 Turnstile 验证区域出现...")
            page.locator("div.g-recaptcha").wait_for(timeout=20000)

            print("点击 Turnstile 验证区域完成验证...")
            page.locator("div.g-recaptcha").click()

            print("等待 8 秒让验证自动完成...")
            time.sleep(8)

            print("填写邮箱和密码...")
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)

            print("提交表单...")
            page.get_by_role("button", name="Submit").click()

            print("等待 6 秒等待页面跳转...")
            time.sleep(6)

            current_url = page.url
            if current_url.strip("/") == SUCCESS_URL.strip("/"):
                print("✅ 登录成功")
            else:
                print(f"❌ 登录失败，当前页面地址：{current_url}")

        except TimeoutError as e:
            print(f"❌ 超时错误: {e}")
        except Exception as e:
            print(f"登录过程中出现错误: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    login()
