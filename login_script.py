import os
from playwright.sync_api import sync_playwright, TimeoutError

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")
LOGIN_URL = "https://betadash.lunes.host/login"
SUCCESS_URL = "https://betadash.lunes.host"  # 登录成功后跳转页面

def login():
    if not EMAIL or not PASSWORD:
        print("未设置登录凭据")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 无头模式
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
            page.wait_for_selector("div.g-recaptcha", timeout=20000)
            page.wait_for_timeout(7000)  # 给7秒自动验证时间

            print("填写邮箱和密码...")
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)

            print("提交表单...")
            with page.expect_navigation(timeout=20000):
                page.click("button[type=submit]")

            current_url = page.url.rstrip("/")
            if current_url == SUCCESS_URL.rstrip("/"):
                print("✅ 登录成功")
            else:
                print(f"❌ 登录失败，当前页面地址：{current_url}")

        except TimeoutError as e:
            print(f"❌ 超时错误: {e}")
        except Exception as e:
            print(f"登录过程异常: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    login()
