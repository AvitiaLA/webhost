from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://betadash.lunes.host/login", timeout=60000)

    frames = page.frames
    print("页面所有 iframe 地址：")
    for f in frames:
        print(f.url)

    browser.close()
