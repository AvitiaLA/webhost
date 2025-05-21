import os
import time
from playwright.sync_api import sync_playwright
from datetime import datetime

# 获取环境变量
EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")

# 登录地址
LOGIN_URL = "https://betadash.lunes.host"

# 截图函数
def take_screenshot(page, label):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"error_{label}_{timestamp}.png"
    try:
        page.screenshot(path=filename)
        print(f"截图保存到 {filename} 以便排查...")
    except Exception as e:
        print("截图失败", e)

# 启动 Playwright 并执行脚本
with sync_playwright() as p:
    try:
        print("启动浏览器...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("访问登录页面...")
        page.goto(LOGIN_URL, timeout=60000)

        # === 处理 Cloudflare Turnstile 验证器 ===
        try:
            print("等待 Cloudflare Turnstile 验证器...")
            iframe_element = page.frame_locator("iframe[title*='security challenge']")
            checkbox = iframe_element.locator("input[type='checkbox']")
            checkbox.wait_for(timeout=20000)
            checkbox.click()
            print("点击了 Cloudflare 验证框，等待验证通过...")
            page.wait_for_timeout(10000)  # 等待跳转完成
        except Exception as e:
            print(f"[警告] 未检测到验证码或处理失败：{e}")

        print("填写邮箱和密码...")
        page.wait_for_selector("#email", timeout=30000)
        page.fill("#email", EMAIL)
        page.fill("#password", PASSWORD)

        print("点击登录按钮...")
        page.click("button[type='submit']")

        print("等待跳转...")
        page.wait_for_url("https://betadash.lunes.host", timeout=20000)

        print("✅ 登录成功！")

    except Exception as e:
        print(f"[错误] 登录过程出错：{e}")
        take_screenshot(page, "login_error")
    finally:
        browser.close()
