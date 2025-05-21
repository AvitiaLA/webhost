import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 环境变量
EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")

START_URL = "https://betadash.lunes.host/login"
LOGIN_URL = "https://betadash.lunes.host/login?next=/"
SUCCESS_URL = "https://betadash.lunes.host"

screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

def save_screenshot(page, prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshot_dir, f"{prefix}_{timestamp}.png")
    try:
        page.screenshot(path=path, full_page=True)
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

            print("等待 Cloudflare Turnstile 验证器...")
            try:
                page.wait_for_timeout(3000)  # 给 iframe 留点加载时间
                frame_locator = page.frame_locator("iframe[title*='security challenge']")
                checkbox = frame_locator.locator("input[type='checkbox']")

                checkbox.wait_for(state="visible", timeout=15000)
                checkbox.click(force=True)
                print("点击验证码复选框成功，等待验证完成...")
                page.wait_for_timeout(5000)  # 等待验证过程（可调）

            except PlaywrightTimeout:
                print("[警告] 验证复选框未出现，可能已跳过验证")
            except Exception as e:
                print(f"[警告] 验证处理失败: {e}")
                save_screenshot(page, "turnstile_error")

            print("填写邮箱和密码...")
            try:
                page.locator("#email").wait_for(state="visible", timeout=20000)
                page.fill("#email", EMAIL)
                page.fill("#password", PASSWORD)
                page.click("button[type='submit']")
            except Exception as e:
                raise Exception(f"表单填写失败: {e}")

            print("等待跳转以确认登录成功...")
            try:
                page.wait_for_url(SUCCESS_URL, timeout=20000)
            except PlaywrightTimeout:
                print(f"[警告] 未跳转到 {SUCCESS_URL}，当前页面: {page.url}")

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
