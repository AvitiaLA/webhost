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
        page.screenshot(path=path, full_page=True)
        print(f"[截图已保存] {path}")
    except Exception as e:
        print("[截图失败]", e)

def click_turnstile_force(page):
    print("尝试强制点击 Cloudflare 验证复选框...")
    try:
        for _ in range(5):
            iframe = page.query_selector("iframe[title*='security challenge']")
            if iframe:
                frame = iframe.content_frame()
                if frame:
                    checkbox = frame.query_selector("input[type='checkbox']")
                    if checkbox:
                        checkbox.click(force=True)
                        print("✅ 成功点击验证码复选框！")
                        return True
            print("等待 iframe 加载...")
            time.sleep(3)
    except Exception as e:
        print("⚠️ 点击验证码复选框失败：", e)
    return False

def wait_for_challenge_pass(page, timeout=30):
    print("等待验证通过（Success!）...")
    for _ in range(timeout):
        content = page.content()
        if "Success!" in content:
            print("✅ Cloudflare 验证通过！")
            return True
        time.sleep(1)
    print("⚠️ 等待超时，未检测到验证通过。")
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

            if not click_turnstile_force(page):
                raise Exception("❌ 验证复选框无法点击")

            if not wait_for_challenge_pass(page):
                raise Exception("❌ Cloudflare 验证未通过")

            print("等待登录表单加载...")
            page.wait_for_selector("#email", timeout=30000)

            print("填写邮箱和密码...")
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)
            page.click("button[type='submit']")

            print("等待登录跳转...")
            page.wait_for_url(SUCCESS_URL, timeout=20000)

            if page.url.startswith(SUCCESS_URL):
                print("✅ 登录成功！")
            else:
                raise Exception(f"❌ 登录失败，URL: {page.url}")

        except Exception as e:
            print("[错误] 登录过程出错：", e)
            save_screenshot(page, "error_login")

        finally:
            browser.close()

if __name__ == "__main__":
    main()
