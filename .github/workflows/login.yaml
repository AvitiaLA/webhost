name: Run Login Script

on:
  workflow_dispatch:
  schedule:
    - cron: "0 0 1 * *"  # 每月1号运行

jobs:
  login:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout 代码
        uses: actions/checkout@v2

      - name: 设置 Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: 安装依赖
        run: |
          python -m pip install --upgrade pip
          pip install playwright requests aiofiles

      - name: 安装 Playwright 浏览器
        run: |
          playwright install

      - name: 运行登录脚本
        env:
          LOGIN_EMAIL: ${{ secrets.LOGIN_EMAIL }}
          LOGIN_PASSWORD: ${{ secrets.LOGIN_PASSWORD }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python login_script.py
