from playwright.sync_api import sync_playwright
import time
import os

# 从环境变量读取账户信息（或直接写死）
EMAIL = os.getenv("LOGIN_EMAIL", "myemail@gmail.com")
PASSWORD = os.getenv("LOGIN_PASSWORD", "YourPasswordHere")

def run():
    with sync_playwright() as p:
        print("启动浏览器...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("访问登录页面...")
            page.goto("https://betadash.lunes.host", timeout=60000)

            # 等待 Cloudflare Turnstile iframe 加载
            print("等待 Cloudflare Turnstile 验证器...")
            turnstile_iframe = page.frame_locator("iframe[title='Widget containing a Cloudflare security challenge']").first
            turnstile_iframe.locator("input[type='checkbox']").wait_for(timeout=15000)

            print("点击 Turnstile 验证框...")
            turnstile_iframe.locator("input[type='checkbox']").click()

            print("等待验证成功标识 'Success!'...")
            page.wait_for_selector("text=Success!", timeout=15000)

            print("填写邮箱和密码...")
            page.fill("#email", EMAIL)
            page.fill("#password", PASSWORD)

            print("点击 Submit 登录按钮...")
            page.get_by_role("button", name="Submit").click()

            print("等待跳转到登录后的页面...")
            page.wait_for_url("https://betadash.lunes.host/**", timeout=20000)

            print("登录成功！当前页面地址：", page.url)

        except Exception as e:
            print(f"[错误] 登录过程出错：{e}")
            print("截图保存到 error.png 以便排查...")
            page.screenshot(path="error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    run()
