import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 环境变量
EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")

START_URL = "https://betadash.lunes.host"
LOGIN_URL = "https://betadash.lunes.host/login?next=/"
SUCCESS_URL = "https://betadash.lunes.host"

screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

def save_screenshot(page, prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshot_dir, f"{prefix}_{timestamp}.png")
    try:
        page.screenshot(path=path)
        print(f"[截图已保存] {path}")
    except Exception as e:
        print("[截图失败]", e)

def main():
    print("启动浏览器...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("访问登录页面...")
            page.goto(START_URL, timeout=60000)
            if page.url != LOGIN_URL:
                print(f"[跳转中] 当前URL: {page.url}，等待登录页面加载...")
                page.wait_for_url(LOGIN_URL, timeout=15000)

            print("等待 Cloudflare Turnstile 验证器...")
            try:
                frame = page.frame_locator("iframe[title*='security challenge']")
                checkbox = frame.locator("input[type='checkbox']")
                checkbox.wait_for(state="visible", timeout=20000)
                checkbox.click()
                print("点击验证码复选框... 等待验证完成")
                page.wait_for_url(LOGIN_URL, timeout=30000)
            except PlaywrightTimeout:
                print("[警告] 未检测到验证码或已跳过验证")

            print("填写邮箱和密码...")
            page.locator("#email").wait_for(state="visible", timeout=30000)
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)
            page.click("button[type='submit']")

            print("等待跳转以确认登录成功...")
            page.wait_for_url(SUCCESS_URL, timeout=15000)

            if page.url.startswith(SUCCESS_URL):
                print("✅ 登录成功！")
            else:
                raise Exception(f"登录失败，当前URL: {page.url}")

        except Exception as e:
            print("[错误] 登录过程出错：", e)
            save_screenshot(page, "error_login")

        finally:
            browser.close()

if __name__ == "__main__":
    main()
