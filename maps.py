from urllib.parse import quote
from playwright.sync_api import Page


class GoogleMaps:

    def __init__(self, page: Page):
        self.page = page

    def search(self, keyword: str):

        url = f"https://www.google.com/maps/search/{quote(keyword)}"

        self.page.goto(url)

        self.page.wait_for_load_state("networkidle")

    def results(self):
        return self.page.locator('a[href*="/place/"]')

    def business_count(self):
        return self.results().count()

    def load_more(self, target=100):

        panel = self.page.locator('div[role="feed"]').first

        last = 0
        stable = 0

        while True:

            count = self.business_count()

            print(f"Loaded: {count}")

            if count >= target:
                break

            if count == last:
                stable += 1
            else:
                stable = 0

            if stable >= 3:
                break

            last = count

            panel.evaluate("(e)=>e.scrollTop=e.scrollHeight")

            self.page.wait_for_timeout(1200)

    def open_business(self, index):

        cards = self.results()

        if index >= cards.count():
            return False

        card = cards.nth(index)

        card.scroll_into_view_if_needed()

        card.click()

        self.page.locator("h1").first.wait_for(timeout=10000)

        return True
