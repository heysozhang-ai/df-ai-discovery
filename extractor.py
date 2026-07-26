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

        business.maps_url = self.page.url

        # ---------------- Name ----------------

        try:
            business.name = (
                self.page.locator("h1").first.inner_text().strip()
            )
        except:
            business.name = ""

        # ---------------- Website ----------------

        try:
            business.website = self.page.locator(
                'a[data-item-id="authority"]'
            ).get_attribute("href") or ""
        except:
            business.website = ""

        # ---------------- Phone ----------------

        try:
            business.phone = self.page.locator(
                'button[data-item-id^="phone"]'
            ).inner_text().strip()
        except:
            business.phone = ""

        # ---------------- Address ----------------

        try:
            business.address = self.page.locator(
                'button[data-item-id="address"]'
            ).inner_text().strip()
        except:
            business.address = ""

        # ---------------- Business Type ----------------

        try:
            buttons = self.page.locator("button")

            for i in range(min(buttons.count(), 30)):

                text = buttons.nth(i).inner_text().strip()

                if (
                    "BMW" in text
                    or "Repair" in text
                    or "Auto" in text
                    or "Mechanic" in text
                    or "Service" in text
                    or "Workshop" in text
                    or "Garage" in text
                ):
                    business.business_type = text
                    break

        except:
            business.business_type = "Unknown"

        if not business.business_type:
            business.business_type = "Unknown"

        # ---------------- Open / Closed ----------------

        try:

            body = self.page.locator("body").inner_text()

            if "Temporarily closed" in body:
                business.is_open = False

            elif "Permanently closed" in body:
                business.is_open = False

            elif "Closed" in body:
                business.is_open = False

            elif "Open" in body:
                business.is_open = True

        except:
            business.is_open = True

        return business
