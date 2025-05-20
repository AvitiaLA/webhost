# login_script.py

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")


async def main():
    print("启动浏览器...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("访问登录页面...")
            await page.goto("https://betadash.lunes.host", timeout=60000)

            print("填写邮箱和密码...")

            await page.get_by_placeholder("myemail@gmail.com").fill(EMAIL)
            await page.get_by_placeholder("Your Password Here").fill(PASSWORD)

            print("等待 Cloudflare Turnstile 验证器...")
            await page.get_by_text("Verify you are human").wait_for(timeout=15000)

            print("点击提交按钮...")
            await page.get_by_role("button", name="Submit").click()

            print("等待跳转或验证登录成功...")
            await page.wait_for_url("https://betadash.lunes.host/", timeout=15000)

            print("✅ 登录成功！")

        except Exception as e:
            print(f"[错误] 登录过程出错：{e}")
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = f"error_{timestamp}.png"
                await page.screenshot(path=path)
                print(f"截图保存到 {path} 以便排查...")
            except Exception as ss:
                print("截图失败", ss)

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
