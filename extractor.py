from playwright.sync_api import Page
from models.business import Business


class BusinessExtractor:

    def __init__(self, page: Page):
        self.page = page

    def open_first_business(self):

        cards = self.page.locator('a[href*="/place/"]')

        cards.first.wait_for(timeout=10000)

        cards.first.click()

        self.page.wait_for_timeout(3000)

    def extract(self):

        business = Business()

        # Name
        try:
            business.name = self.page.locator("h1").last.inner_text().strip()
        except:
            pass

        # Website
        try:
            business.website = self.page.locator(
                'a[data-item-id="authority"]'
            ).get_attribute("href")
        except:
            pass

        # Google Maps URL
        business.maps_url = self.page.url

        # Open / Closed
        try:
            text = self.page.locator("body").inner_text()

            if "Open" in text and "Closed" not in text:
                business.is_open = True

        except:
            pass

        return business
