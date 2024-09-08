from subprocess import run
from playwright.sync_api import sync_playwright
from playwright._impl._errors import Error as BrowserType_launch
from playwright._impl._errors import TimeoutError as BrowserTimeout


cookie_path = '.whatsapp_cookies'


def whatsapp_sender(receiver, message):
    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch_persistent_context(user_data_dir=cookie_path, headless=True, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")
        try:
            page.locator('xpath=//span[@data-icon="chats-filled"]').wait_for(state='visible', timeout=10000)
        except BrowserTimeout:
            return False

        page.locator('xpath=//div[@id="side"]/div/div/div/div/div/div/p[contains(@class, "selectable-text")]').fill(receiver)
        page.locator(f'xpath=//span[@title="{receiver.title().replace(" ", "", 1)}"]').click()
        page.locator('xpath=//div[@id="main"]/footer/div/div/span/div/div/div/div/div/p[contains(@class, "selectable-text")]').fill(message)
        page.locator('xpath=//span[@data-icon="send"]').click()
        page.locator(f'(//span[text()="{message}"])[2]/../../../../../div/div/div/div/span[@data-icon="msg-check"]').wait_for(state='visible', timeout=3000)


def whatsapp_cookie_maker():
    try:
        whatsapp_cookie_maker_browser_actions()
    except BrowserType_launch:
        run(['playwright', 'install'])
        whatsapp_cookie_maker_browser_actions()


def whatsapp_cookie_maker_browser_actions():
    with sync_playwright() as playwright:
        chromium = playwright.chromium
        browser = chromium.launch_persistent_context(user_data_dir=cookie_path, headless=False)
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")
        element = page.locator('xpath=//p[contains(@class, "selectable-text")]')
        element.wait_for(state='visible')
