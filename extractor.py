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

        # ---------- Name ----------

        business.name = ""

        try:

            h1 = self.page.locator("h1").first.inner_text().strip()

            if h1 and h1.lower() != "results":

                business.name = h1

        except:

            pass

        if not business.name:

            try:

                title = self.page.title()

                if " - Google Maps" in title:

                    business.name = title.replace(" - Google Maps", "").strip()

            except:

                pass

        # ---------- Website ----------

        business.website = ""

        try:

            business.website = (

                self.page.locator(

                    'a[data-item-id="authority"]'

                ).get_attribute("href")

                or ""

            )

        except:

            pass

        # ---------- Phone ----------

        business.phone = ""

        try:

            business.phone = (

                self.page.locator(

                    'button[data-item-id^="phone"]'

                ).inner_text().strip()

            )

        except:

            pass

        # ---------- Address ----------

        business.address = ""

        try:

            business.address = (

                self.page.locator(

                    'button[data-item-id="address"]'

                ).inner_text().strip()

            )

        except:

            pass

        # ---------- Business Type ----------

        business.business_type = "Unknown"

        try:

            chips = self.page.locator('button[jsaction]')

            keywords = [

                "Repair",

                "Service",

                "Auto",

                "Mechanic",

                "Garage",

                "European",

                "BMW",

                "Transmission",

                "Tire",

                "Oil",

                "Body",

            ]

            for i in range(min(chips.count(), 50)):

                text = chips.nth(i).inner_text().strip()

                if len(text) > 40:

                    continue

                if any(k.lower() in text.lower() for k in keywords):

                    business.business_type = text

                    break

        except:

            pass

        # ---------- Open Status ----------

        business.is_open = True

        try:

            status = self.page.locator(

                'div[aria-label*="Open"], div[aria-label*="Closed"]'

            ).first.inner_text()

            status = status.lower()

            if "temporarily closed" in status:

                business.is_open = False

            elif "permanently closed" in status:

                business.is_open = False

            elif "closed" in status:

                business.is_open = False

            elif "open" in status:

                business.is_open = True

        except:

            pass

        return business
