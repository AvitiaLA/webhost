import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

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
        page.screenshot(path=path)
        print(f"[截图已保存] {path}")
    except Exception as e:
        print("[截图失败]", e)

def wait_for_turnstile(page):
    print("等待 Cloudflare Turnstile 验证器 iframe 出现...")
    try:
        # 最长等待 30 秒加载 iframe
        for _ in range(30):
            frames = page.frames
            for frame in frames:
                if "Challenge" in frame.title() or "challenge" in frame.url:
                    checkbox = frame.locator("input[type='checkbox']")
                    try:
                        checkbox.wait_for(state="visible", timeout=2000)
                        checkbox.click()
                        print("✅ 成功点击验证码复选框")
                        return True
                    except:
                        pass
            print("等待验证码 iframe 加载中...")
            time.sleep(1)
    except Exception as e:
        print("[错误] 验证处理失败：", e)
    return False

def wait_for_success_text(page):
    try:
        print("等待 Cloudflare 验证通过的标志 'Success!' 出现...")
        page.wait_for_selector("text=Success!", timeout=15000)
        print("✅ 验证通过！")
        return True
    except:
        print("[警告] 未检测到 'Success!'，可能验证已跳过或失败")
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

            print("处理 Cloudflare Turnstile 验证...")
            verified = wait_for_turnstile(page)
            if not verified:
                raise Exception("❌ 验证复选框无法点击")

            wait_for_success_text(page)

            print("等待登录表单加载...")
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
