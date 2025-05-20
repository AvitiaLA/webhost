import asyncio
from playwright.async_api import async_playwright
import os

EMAIL = os.getenv("LOGIN_EMAIL")
PASSWORD = os.getenv("LOGIN_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LOGIN_URL = "https://betadash.lunes.host"
SUCCESS_URL = "https://betadash.lunes.host/"

async def send_telegram_message(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[警告] Telegram 配置缺失，无法发送消息。")
        return
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        print("[Telegram] 已发送消息")
    except Exception as e:
        print(f"[Telegram] 消息发送失败: {e}")

async def main():
    try:
        print("启动浏览器...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            print("访问登录页面...")
            await page.goto(LOGIN_URL, timeout=60000)

            print("填写邮箱和密码...")
            await page.fill("#email", EMAIL)
            await page.fill("#password", PASSWORD)

            print("等待 Cloudflare Turnstile 验证器加载...")
            await page.wait_for_selector("iframe[title*='Cloudflare']", timeout=20000)

            print("点击验证码 checkbox...")
            turnstile_frame = page.frame_locator("iframe[title*='Cloudflare']").first
            await turnstile_frame.locator("input[type='checkbox']").click()

            print("等待验证成功 'Success!' 出现...")
            await page.wait_for_selector("text=Success!", timeout=15000)

            print("点击 Submit 登录按钮...")
            await page.get_by_role("button", name="Submit").click()

            print("等待跳转到主页...")
            await page.wait_for_url(SUCCESS_URL, timeout=15000)

            print("[成功] 登录成功！")
            await send_telegram_message("✅ 登录成功！🎉")
            await browser.close()

    except Exception as e:
        print(f"[错误] 登录过程出错：{e}")
        try:
            await page.screenshot(path="error.png")
            print("截图保存到 error.png 以便排查...")
        except:
            print("截图失败")
        await send_telegram_message(f"❌ 登录失败！错误信息：{e}")

if __name__ == "__main__":
    asyncio.run(main())
