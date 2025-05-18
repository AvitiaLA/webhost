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
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(LOGIN_URL, timeout=60000)
            print("页面加载完成")

            # 直接等待页面上的 Cloudflare 验证复选框出现并点击
            print("等待 Cloudflare 验证复选框出现...")
            checkbox = page.locator("role=checkbox")
            checkbox.wait_for(timeout=15000)
            checkbox.click()
            print("Cloudflare 验证复选框已点击")
            time.sleep(5)  # 等待验证过程结束

            # 填写登录信息
            page.get_by_placeholder("myemail@gmail.com").fill(EMAIL)
            page.get_by_placeholder("Your Password Here").fill(PASSWORD)

            # 提交登录
            with page.expect_navigation(timeout=15000):
                page.get_by_role("button", name="Submit").click()

            # 判断是否跳转成功
            current_url = page.url
            if current_url.strip("/") == SUCCESS_URL.strip("/"):
                print("✅ 登录成功")
            else:
                print(f"❌ 登录失败: 未跳转到仪表板页面 ({current_url})")

        except TimeoutError as e:
            print(f"❌ 超时错误: {e}")
        except Exception as e:
            print(f"登录过程中出现错误: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    login()
