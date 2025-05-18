import os
from playwright.sync_api import sync_playwright, TimeoutError

def login():
    email = os.getenv("LOGIN_EMAIL")
    password = os.getenv("LOGIN_PASSWORD")
    if not email or not password:
        print("请设置环境变量 LOGIN_EMAIL 和 LOGIN_PASSWORD")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://betadash.lunes.host/login")

        page.fill("#email", email)
        page.fill("#password", password)

        try:
            frame_element = page.wait_for_selector("iframe[src*='challenges.cloudflare.com']", timeout=15000)
        except TimeoutError:
            print("验证iframe未出现，可能不需要验证")
            browser.close()
            return False

        frame = frame_element.content_frame()
        if not frame:
            print("获取iframe失败")
            browser.close()
            return False

        try:
            checkbox = frame.wait_for_selector("div.cf-turnstile-checkbox", timeout=10000)
            checkbox.click()
            print("复选框点击完成，等待验证结果...")
        except TimeoutError:
            print("验证复选框未找到或点击失败")
            browser.close()
            return False

        try:
            page.wait_for_url("https://betadash.lunes.host/dashboard", timeout=20000)
            print("登录成功！")
            return True
        except TimeoutError:
            print("未跳转到仪表盘页面，登录失败")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    login()
