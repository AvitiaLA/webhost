import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
import time

try:
    import selenium
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])

def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def login_koyeb(email, password):
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    try:
        driver.get("https://betadash.lunes.host/login")

        # 输入邮箱和密码
        email_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='myemail@gmail.com']")
        email_field.send_keys(email)
        password_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Your Password Here']")
        password_field.send_keys(password)

        # 定位 Cloudflare 验证复选框
        checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='Verify you are human']"))
        )

        # 点击复选框
        checkbox.click()

        # 点击登录按钮
        login_button = driver.find_element(By.CSS_SELECTOR, "button[name='Submit']")
        login_button.click()

        # 等待可能出现的错误消息或成功登录后的页面
        try:
            # 等待可能的错误消息
            error_message = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiAlert-message"))
            )
            error_text = error_message.text
            return f"账号 {email} 登录失败: {error_text}"
        except:
            # 如果没有找到错误消息,检查是否已经跳转到仪表板页面
            try:
                WebDriverWait(driver, 10).until(
                    EC.url_contains("https://betadash.lunes.host")
                )
                return f"账号 {email} 登录成功!"
            except:
                return f"账号 {email} 登录失败: 未能跳转到仪表板页面"
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        import selenium
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])

    accounts = os.environ.get('WEBHOST', '').split()
    login_statuses = []

    for account in accounts:
        email, password = account.split(':')
        status = login_koyeb(email, password)
        login_statuses.append(status)
        print(status)

    if login_statuses:
        message = "WEBHOST登录状态:\n\n" + "\n".join(login_statuses)
        result = send_telegram_message(message)
        print("消息已发送到Telegram:", result)
    else:
        print("没有登录状态信息")
