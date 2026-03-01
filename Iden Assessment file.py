import os
import json
from playwright.sync_api import sync_playwright

BASE_URL = "https://hiring.idenhq.com/"
EMAIL = "harishviswa2020@gmail.com"
PASSWORD = "R6YfktVG"

SESSION_FILE = "session_state.json"
OUTPUT_FILE = "products.json"


def create_authenticated_context(playwright):
    browser = playwright.chromium.launch(headless=False)

    if os.path.exists(SESSION_FILE):
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        page.goto(BASE_URL)

        if "login" not in page.url.lower():
            return browser, context, page

    context = browser.new_context()
    page = context.new_page()
    page.goto(BASE_URL)

    page.fill("input[type='email']", EMAIL)
    page.fill("input[type='password']", PASSWORD)
    page.click("button:has-text('Sign in')")
    page.wait_for_load_state("networkidle")

    context.storage_state(path=SESSION_FILE)

    return browser, context, page


def navigate_to_product_table(page):
    page.get_by_text("Dashboard").click()
    page.wait_for_timeout(1000)

    page.get_by_text("Inventory").click()
    page.wait_for_timeout(1000)

    page.get_by_text("Catalog").click()
    page.wait_for_timeout(1000)

    page.get_by_text("View Complete Data").click()
    page.wait_for_load_state("networkidle")


def load_all_products(page):
    previous_count = 0

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

        current_count = page.locator("div:has-text('Manufacturer')").count()

        if current_count == previous_count:
            break

        previous_count = current_count


def extract_product_data(page):
    products = []
    cards = page.locator("div:has-text('Manufacturer')")

    for i in range(cards.count()):
        card = cards.nth(i)
        lines = card.inner_text().split("\n")

        if len(lines) >= 8:
            product = {
                "name": lines[0].strip(),
                "id": lines[1].strip(),
                "manufacturer": lines[3].strip(),
                "guarantee": lines[5].strip(),
                "cost": lines[7].strip()
            }
            products.append(product)

    return products


def main():
    with sync_playwright() as playwright:
        browser, context, page = create_authenticated_context(playwright)

        navigate_to_product_table(page)
        load_all_products(page)

        product_data = extract_product_data(page)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(product_data, file, indent=4)

        browser.close()


if __name__ == "__main__":
    main()