import os
import requests
import time
from selenium import webdriver
# 导入BY
from selenium.webdriver.common.by import By
# 导入Keys
from selenium.webdriver.common.keys import Keys


def login(username,password,url="https://webvpn.bit.edu.cn"):
    # 启动selenium
    options = webdriver.ChromeOptions()
    # 无头模式
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3') # 不要输出日志
    browser = webdriver.Chrome(options=options)
    browser.get(url)
    # 输入用户名
    username_input = browser.find_element(By.ID,"username")
    username_input.send_keys(username)
    # 输入密码
    password_input = browser.find_element(By.ID,"password")
    password_input.send_keys(password)
    # 点击登录
    login_button = browser.find_element(By.ID,"login_submit")
    login_button.click()
    # 获取cookies
    cookies = browser.get_cookies()
    # 保存cookies为字符串
    cookies_str = ""
    for cookie in cookies:
        cookies_str += cookie["name"] + "=" + cookie["value"] + ";"
    # 关闭浏览器
    browser.quit()
    return cookies_str
