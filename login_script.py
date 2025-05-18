import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")
LOGIN_URL = "https://betadash.lunes.host/login"
SUCCESS_URL = "https://betadash.lunes.host"

def login():
    if not EMAIL or not PASSWORD:
        print("❌ 未设置登录凭据")
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
            print("\n访问登录页面...")
            page.goto(LOGIN_URL, timeout=60000)

            print("等待 Turnstile 验证区域 iframe 出现...")
            iframe_locator = page.locator("iframe[src*='challenges.cloudflare.com']")
            iframe_locator.wait_for(timeout=15000)

            print("点击 Turnstile 验证区域触发验证...")
            box = iframe_locator.bounding_box()
            if box:
                page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                time.sleep(6)  # 等待验证完成
            else:
                print("❌ 无法获取 iframe 的位置，跳过点击")

            print("填写邮箱和密码...")
            page.get_by_placeholder("myemail@gmail.com").fill(EMAIL)
            page.get_by_placeholder("Your Password Here").fill(PASSWORD)

            print("提交表单...")
            page.get_by_role("button", name="Submit").click()

            print("等待页面跳转...")
            time.sleep(6)  # 等待跳转完成（重要）

            current_url = page.url
            if current_url.strip("/").startswith(SUCCESS_URL.strip("/")):
                print("✅ 登录成功")
            else:
                print(f"❌ 登录失败，当前页面地址：{current_url}")

        except TimeoutError as te:
            print(f"❌ 超时错误: {te}")
        except Exception as e:
            print(f"❌ 登录过程中出现错误: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    login()
