import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")
LOGIN_URL = "https://betadash.lunes.host/login"
SUCCESS_URL = "https://betadash.lunes.host"  # 登录成功跳转地址

def login():
    if not EMAIL or not PASSWORD:
        print("未设置登录凭据")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("访问登录页面...")
            page.goto(LOGIN_URL, timeout=60000)

            print("等待 Turnstile 验证组件加载...")
            # 等待 Turnstile 验证 div 里出现 iframe (Turnstile 通常会注入 iframe)
            page.wait_for_selector("div.g-recaptcha iframe", timeout=20000)
            print("Turnstile 验证组件加载完成")

            # 填写账号密码
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)

            print("提交登录表单...")
            with page.expect_navigation(timeout=20000):
                page.click("button[type=submit]")

            # 登录后判断页面地址
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
