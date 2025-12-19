"""
Utility functions for webdriver setup and management
Windows (local) + Render (Docker/Linux) compatible
"""

import os
import platform
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def setup_webdriver():
    """
    Starts Chrome WebDriver safely.

    - Windows: uses local chromedriver.exe + installed Chrome
    - Render/Linux (Docker): uses system chromium + chromedriver
    """

    options = Options()

    # Common required flags
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    system = platform.system()

    try:
        # =========================
        # WINDOWS (LOCAL)
        # =========================
        if system == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]

            chrome_binary = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    break

            if not chrome_binary:
                st.error("Google Chrome not found on this system")
                return None

            options.binary_location = chrome_binary

            driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
            if not os.path.exists(driver_path):
                st.error("chromedriver.exe not found in project root")
                return None

            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)

            st.success("Chrome WebDriver started on Windows")
            return driver

        # =========================
        # LINUX / RENDER (DOCKER)
        # =========================
        else:
            # Docker already installs chromium + chromedriver
            driver = webdriver.Chrome(options=options)
            st.success("Chrome WebDriver started on Render / Docker")
            return driver

    except Exception as e:
        st.error(f"WebDriver failed: {e}")
        return None
