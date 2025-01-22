import asyncio
from fake_useragent import UserAgent
from playwright.async_api import async_playwright
import os


async def page_launch_playwright():

    playwright = await async_playwright().start()
    device = playwright.devices['Desktop Chrome']
    device['user_agent'] = UserAgent().firefox
    device['viewport'] = {'width': 1366, 'height': 768}

    bytes_read = bytes
    pfx_file_path = os.path.abspath("C:\\dev\\__bite_dev\\PROJGosZakupAutomation\\cert\\GOST512_02213f9c53acb47ee1fc17fa8592e2bd0b98df29.p12")
    with open(pfx_file_path, "rb") as f:
        bytes_read = f.read()  



    # Ensure the certificate is correctly attached
    device["client_certificates"] = [
        {
            "origin": 'https://v3bl.goszakup.gov.kz',
            "pfx": bytes_read,  # Ensure you are passing the correct absolute path
            "passphrase": 'Aa1234',  # Correct passphrase for the certificate
            "ciphers": "DEFAULT:@SECLEVEL=0",
        }
    ]

    url_base_path = "https://v3bl.goszakup.gov.kz"

    launch_config = {
        "headless": False,
        "timeout": 10000,
        "proxy": None,
        "slow_mo": 190
    }

    browser = await playwright.firefox.launch(**launch_config)

    context = await browser.new_context(**device)

    print("Loaded client certificates: ", context.client_certificates())

    await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    page_driver = await context.new_page()

    await page_driver.goto(url_base_path)

    await page_driver.wait_for_timeout(5000)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(page_launch_playwright())