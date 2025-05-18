import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")
LOGIN_URL = "https://betadash.lunes.host/login"
SUCCESS_URL = "https://betadash.lunes.host"

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

            # 等待 iframe 出现（先等待 iframe 元素）
            print("等待 Cloudflare 验证 iframe 出现...")
            iframe_element = page.wait_for_selector("iframe[src*='challenges.cloudflare.com']", timeout=30000)
            print("iframe 元素出现，获取 frame 对象...")
            frame = iframe_element.content_frame()
            if not frame:
                raise Exception("iframe的内容frame没有加载出来")

            print("等待复选框出现...")
            checkbox = frame.wait_for_selector("role=checkbox", timeout=20000)
            print("复选框出现，点击复选框...")
            checkbox.click()
            print("复选框已点击，等待验证完成...")
            time.sleep(7)

            # 填写登录信息
            page.get_by_placeholder("myemail@gmail.com").fill(EMAIL)
            page.get_by_placeholder("Your Password Here").fill(PASSWORD)

            # 提交登录
            with page.expect_navigation(timeout=15000):
                page.get_by_role("button", name="Submit").click()

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
