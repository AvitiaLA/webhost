import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")
LOGIN_URL = "https://betadash.lunes.host/login"
SUCCESS_URL = "https://betadash.lunes.host"  # 登录成功后跳转的页面

def login():
    if not EMAIL or not PASSWORD:
        print("未设置登录凭据")
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

            print("等待 Turnstile 自动验证完成...")
            time.sleep(8)

            print("填写邮箱和密码...")
            page.get_by_placeholder("myemail@gmail.com").fill(EMAIL)
            page.get_by_placeholder("Your Password Here").fill(PASSWORD)

            print("提交表单...")
            page.get_by_role("button", name="Submit").click()

            print("等待页面跳转...")
            time.sleep(6)  # 等待登录处理完成

            current_url = page.url
            if current_url.strip("/") == SUCCESS_URL.strip("/"):
                print("✅ 登录成功")
            else:
                print(f"❌ 登录失败，当前页面地址：{current_url}")

        except TimeoutError as te:
            print(f"❌ 超时错误: {te}")
        except Exception as e:
            print(f"登录过程中出现错误: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    login()
