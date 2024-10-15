import json
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync


def save_cookies(page, cookies_file):
    cookies = page.context.cookies()
    with open(cookies_file, 'w') as f:
        json.dump(cookies, f)


def navigate_to_deals(postal_code, cookies_file) : 
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # Example of Chrome user agent
            viewport={"width": 1280, "height": 720}
        )

        page = context.new_page()

         # Apply stealth mode to avoid detection
        #stealth_sync(page)

        # Remove WebDriver property to avoid detection
        page.evaluate("() => delete navigator.webdriver")

        # Check if cookies exist to load
        try:
            with open(cookies_file, 'r') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)

        except FileNotFoundError:

            #Go to provigo home page
            page.goto("https://www.provigo.ca/")

            page.set_default_navigation_timeout(60000)  # Set a longer timeout

            #Click the current address button 
            page.wait_for_selector('button[data-cruller="fulfillment-mode-button"]')
            page.click('button[data-cruller="fulfillment-mode-button"]', delay=500)

            # Step 3: Click "Change Location" link in the popup
            page.wait_for_selector('a[data-cruller="store-locator-link"]')
            page.click('a[data-cruller="store-locator-link"]', delay=500)

            # Step 4: Enter postal code or address in the store locator
            page.goto("https://www.provigo.ca/store-locator?type=store&icta=pickup-details-modal")
            page.fill('input[id="location-search__search__input"]', postal_code)
            page.keyboard.press("Enter", delay=500)

            # Step 5: Choose a store from the list
            page.wait_for_selector('button[data-track="storeLocatorShopNowResetButton"]')
            page.click('button[data-track="storeLocatorShopNowResetButton"]', delay=500)

            # Step 6: Click "Continue shopping" in the final popup
            page.wait_for_selector('a[data-track="fulfillmentLocationConfirmationContinueButton"]')
            page.click('a[data-track="fulfillmentLocationConfirmationContinueButton"]', delay=500)

            # Save cookies after successful location setup
            save_cookies(page, cookies_file)

        # Step 7: Navigate to the deals page
        page.goto("https://www.provigo.ca/deals/all?navid=flyout-L2-All-Deals")
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(120000)

        # Confirm the page loaded
        print(page.title())
        #page.wait_for_selector('button[data-cruller="fulfillment-mode-button"]')
        #print(page.query_selector('div[data-cruller="current-location"]').inner_text())

        return browser, page, playwright