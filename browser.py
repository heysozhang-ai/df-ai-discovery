from playwright.sync_api import sync_playwright

class BrowserManager:

    def __init__(self, headless=False):

        self.headless = headless

        self.playwright = None

        self.browser = None

        self.page = None

    def start(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(

            headless=self.headless

        )

        self.page = self.browser.new_page(

            viewport={"width": 1600, "height": 900}

        )

        return self.page

    def new_page(self):

        page = self.browser.new_page(

            viewport={"width": 1600, "height": 900}

        )

        page.set_default_timeout(8000)

        page.set_default_navigation_timeout(8000)

        return page

    def close_page(self, page):

        try:

            if page and not page.is_closed():

                page.close()

        except:

            pass

    def close(self):

        if self.browser:

            self.browser.close()

        if self.playwright:

            self.playwright.stop()
