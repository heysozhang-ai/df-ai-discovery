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

            panel.evaluate("(e)=>e.scrollTop=e.scrollHeight")

            self.page.wait_for_timeout(500)

    def open_business(self, index):

        try:

            cards = self.results()

            if index >= cards.count():
                return False

            card = cards.nth(index)

            card.scroll_into_view_if_needed()

            self.page.wait_for_timeout(200)

            # 第一次点击
            card.click(timeout=5000)

            try:
                self.page.locator("h1").first.wait_for(timeout=3000)
                return True
            except:
                pass

            # 第二次点击
            card.click(timeout=5000, force=True)

            self.page.locator("h1").first.wait_for(timeout=5000)

            return True

        except Exception as e:

            print(f"Open failed: {e}")

            return False

    def back_to_results(self):

        try:

            back = self.page.locator('button[aria-label="Back"]').first

            if back.is_visible(timeout=1000):
                back.click(timeout=3000)
            else:
                self.page.go_back()

        except:

            try:
                self.page.go_back()
            except:
                pass

        try:
            self.page.locator('div[role="feed"]').first.wait_for(timeout=5000)
        except:
            pass

        self.page.wait_for_timeout(300)
