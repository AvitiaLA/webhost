import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 环境变量
EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")

START_URL = "https://betadash.lunes.host/login"
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

def wait_for_cloudflare(page):
    print("等待 Cloudflare 验证完成...")
    try:
        # 等待 “Verify you are human” 消失 或 “Success!” 出现
        for i in range(30):  # 最多等30秒
            content = page.content()
            if "Success!" in content:
                print("✅ Cloudflare 验证成功！")
                return True
            if "Verify you are human" not in content:
                print("✅ Cloudflare 验证已跳过或已完成！")
                return True
            time.sleep(1)
        print("[超时] Cloudflare 验证未完成")
        return False
    except Exception as e:
        print("[异常] 验证检测失败：", e)
        return False

def main():
    print("启动浏览器...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("访问登录页面...")
            page.goto(START_URL, timeout=60000)

            if not wait_for_cloudflare(page):
                raise Exception("Cloudflare 验证未通过")

            print("等待登录表单加载...")
            page.wait_for_selector("#email", timeout=20000)
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)
            page.click("button[type='submit']")

            print("等待跳转以确认登录成功...")
            page.wait_for_url(SUCCESS_URL, timeout=20000)

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
