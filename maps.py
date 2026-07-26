from urllib.parse import quote
from playwright.sync_api import Page, TimeoutError


class GoogleMaps:

    def __init__(self, page: Page):
        self.page = page

    def search(self, keyword: str):

        url = f"https://www.google.com/maps/search/{quote(keyword)}"

        self.page.goto(url, wait_until="domcontentloaded")

        self.page.locator('div[role="feed"]').first.wait_for(timeout=15000)

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

            if stable >= 5:
                print("No more results.")
                break

            last = count

            panel.evaluate("(e) => e.scrollTop = e.scrollHeight")

            self.page.wait_for_timeout(800)

    def open_business(self, index):

        cards = self.results()

        if index >= cards.count():
            return False

        for attempt in range(3):
            try:
                cards = self.results()

                card = cards.nth(index)

                card.scroll_into_view_if_needed()

                self.page.wait_for_timeout(300)

                card.click(timeout=5000)

                self.page.locator("h1").first.wait_for(timeout=10000)

                return True

            except TimeoutError:
                print(f"Retry open business {index} ({attempt + 1}/3)")
                self.page.wait_for_timeout(1000)

            except Exception as e:
                print(f"Open failed: {e}")
                self.page.wait_for_timeout(1000)

        return False

    def back_to_results(self):

        self.page.go_back(wait_until="domcontentloaded")

        self.page.locator('div[role="feed"]').first.wait_for(timeout=15000)

        self.page.wait_for_timeout(1000)
