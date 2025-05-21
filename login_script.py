import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 环境变量读账号密码，确保你运行前先 export LOGIN_EMAIL 和 LOGIN_PASSWORD
EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")

START_URL = "https://betadash.lunes.host/login"
SUCCESS_URL = "https://betadash.lunes.host"

screenshot_dir = "screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

def save_screenshot(page, prefix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{screenshot_dir}/{prefix}_{timestamp}.png"
    try:
        page.screenshot(path=path)
        print(f"[截图已保存] {path}")
    except Exception as e:
        print("[截图失败]", e)

def wait_for_turnstile(page):
    print("等待 Cloudflare Turnstile 验证器 iframe 出现...")
    for attempt in range(30):
        frames = page.frames
        print(f"[调试] 尝试第 {attempt+1} 次，当前页面共有 {len(frames)} 个 frame:")
        for i, frame in enumerate(frames):
            print(f"  frame[{i}] URL: {frame.url}, Title: {frame.title()}")

        for frame in frames:
            if "Challenge" in frame.title() or "challenge" in frame.url:
                checkbox = frame.locator("input[type='checkbox']")
                count = checkbox.count()
                print(f"[调试] 找到验证码 iframe，复选框数量: {count}")
                if count > 0:
                    try:
                        checkbox.wait_for(state="visible", timeout=3000)
                        # 使用JS点击复选框，避免点击失败
                        frame.evaluate("(checkbox) => checkbox.click()", checkbox.element_handle())
                        print("✅ 通过JS点击验证码复选框成功")
                        return True
                    except Exception as e:
                        print(f"[调试] JS点击复选框失败: {e}")
        print("等待验证码 iframe 加载中...")
        time.sleep(1)
    return False

def wait_for_success_text(page):
    try:
        print("等待 Cloudflare 验证通过的标志 'Success!' 出现...")
        page.wait_for_selector("text=Success!", timeout=15000)
        print("✅ 验证通过！")
        return True
    except PlaywrightTimeout:
        print("[警告] 未检测到 'Success!'，可能验证已跳过或失败")
        return False

def main():
    print("启动浏览器...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 运行时看得见浏览器方便调试
        context = browser.new_context()
        page = context.new_page()

        try:
            print("访问登录页面...")
            page.goto(START_URL, timeout=60000)

            print("处理 Cloudflare Turnstile 验证...")
            if not wait_for_turnstile(page):
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
