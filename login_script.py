import os
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

def try_click_turnstile_checkbox(page):
    print("尝试点击 Cloudflare 验证复选框...")
    try:
        iframe_element = page.locator("iframe[title*='security challenge']")
        iframe_element.wait_for(state="visible", timeout=15000)

        frame = iframe_element.content_frame()
        checkbox = frame.locator("input[type='checkbox']")
        checkbox.wait_for(state="visible", timeout=15000)
        checkbox.click(force=True)
        print("✅ 成功点击 Cloudflare 复选框！")
        return True
    except Exception as e:
        print("[警告] 无法点击 Cloudflare 验证复选框：", e)
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

            # 点击 Cloudflare 验证
            clicked = try_click_turnstile_checkbox(page)
            if not clicked:
                raise Exception("❌ 验证复选框未成功点击，脚本终止。")

            print("等待登录表单加载...")
            page.wait_for_selector("#email", timeout=30000)

            print("填写邮箱和密码...")
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)
            page.click("button[type='submit']")

            print("等待登录跳转...")
            page.wait_for_url(SUCCESS_URL, timeout=15000)

            if page.url.startswith(SUCCESS_URL):
                print("✅ 登录成功！")
            else:
                raise Exception(f"❌ 登录后未跳转成功页面，当前URL: {page.url}")

        except Exception as e:
            print("[错误] 登录过程出错：", e)
            save_screenshot(page, "error_login")

        finally:
            browser.close()

if __name__ == "__main__":
    main()
