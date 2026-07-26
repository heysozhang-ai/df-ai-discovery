from playwright.sync_api import sync_playwright


class BrowserManager:

    def __init__(self, headless=False):

        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self._context = None

    def start(self):

        self.playwright = sync_playwright().start()
        self._launch()
        self.page = self.new_page()
        return self.page

    def _launch(self):

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--js-flags=--max-old-space-size=512",
            ],
        )
        self._context = self.browser.new_context(
            viewport={"width": 1600, "height": 900},
        )

    def ensure_browser(self):

        if self.browser and self.browser.is_connected():
            return

        self._launch()

    def new_page(self, block_media=False):

        self.ensure_browser()

        if self._context is None or not self.browser.is_connected():
            self._launch()

        page = self._context.new_page()
        page.set_default_timeout(8000)
        page.set_default_navigation_timeout(15000)

        if block_media:
            page.route(
                "**/*",
                lambda route: (
                    route.abort()
                    if route.request.resource_type in ("image", "media", "font")
                    else route.continue_()
                ),
            )

        return page

    def ensure_page(self, page, block_media=False):

        try:
            if page and not page.is_closed():
                return page
        except Exception:
            pass

        return self.new_page(block_media=block_media)

    def close_page(self, page):

        try:
            if page and not page.is_closed():
                page.close()
        except Exception:
            pass

    def close(self):

        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
        self._context = None

        try:
            if self.browser and self.browser.is_connected():
                self.browser.close()
        except Exception:
            pass
        self.browser = None
        self.page = None

        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass
            self.playwright = None
