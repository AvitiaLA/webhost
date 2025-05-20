import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

EMAIL = os.getenv("LOGIN_EMAIL", "myemail@gmail.com")
PASSWORD = os.getenv("LOGIN_PASSWORD", "Your Password Here")

async def main():
    print("启动浏览器...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("访问登录页面...")
            await page.goto("https://betadash.lunes.host", timeout=60000)

            # --- 替换这里：Cloudflare Turnstile 验证框检测和点击 ---
            print("等待 Cloudflare Turnstile 验证 iframe 加载...")
            try:
                turnstile_frame = page.frame_locator("iframe[src*='turnstile']")
                checkbox = turnstile_frame.locator("input[type=checkbox]")
                await checkbox.wait_for(timeout=15000)
                print("点击 Turnstile 复选框...")
                await checkbox.click()
                await page.wait_for_timeout(5000)  # 等待验证完成
            except Exception:
                print("⚠️ 未检测到 Turnstile 验证框，可能已通过或不存在")
            # ------------------------------------------------------

            print("填写邮箱和密码...")
            await page.get_by_placeholder("myemail@gmail.com").fill(EMAIL)
            await page.get_by_placeholder("Your Password Here").fill(PASSWORD)

            print("点击提交按钮...")
            await page.get_by_role("button", name="Submit").click()

            print("等待跳转...")
            await page.wait_for_url("**/dashboard", timeout=15000)
            print("✅ 登录成功！当前页面：", page.url)

        except Exception as e:
            print(f"[错误] 登录过程出错：{e}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"error_{timestamp}.png"
            try:
                await page.screenshot(path=screenshot_path)
                print(f"截图保存到 {screenshot_path} 以便排查...")
            except:
                print("截图失败")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
