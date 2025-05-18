import time
import os
import telegram
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

EMAIL = os.getenv("LOGIN_EMAIL", "your-email@example.com")
PASSWORD = os.getenv("LOGIN_PASSWORD", "your-password")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("未设置 Telegram 配置")
        return {"ok": False, "description": "Missing token or chat_id"}
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        return {"ok": False, "description": str(e)}


def login():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = uc.Chrome(options=options)
        driver.get("https://lunes.host/login")

        # 填写邮箱和密码
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        # 等待复选框 iframe 加载
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[src*='challenges.cloudflare.com']"))
        )

        # 点击复选框
        checkbox = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox']"))
        )
        checkbox.click()

        # 返回主页面继续提交
        driver.switch_to.default_content()

        # 点击提交按钮
        submit = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        submit.click()

        # 检查是否成功跳转到仪表板
        WebDriverWait(driver, 15).until(
            EC.url_contains("/dashboard")
        )
        print("✅ 登录成功！")
        send_telegram_message("✅ 登录成功！")
        driver.quit()
        return True
    except Exception as e:
        print("账号  登录失败:", str(e))
        send_telegram_message(f"账号  登录失败: {e}")
        driver.quit()
        return False


if __name__ == "__main__":
    login()
