from urllib.parse import quote

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


class GoogleMaps:

    def __init__(self, page: Page):
        self.page = page
        self._urls = []
        self._seen_paths = set()
        self._feed = None
        self._place_links = None

    def _cache_locators(self):
        self._feed = self.page.locator('div[role="feed"]').first
        self._place_links = self.page.locator('a[href*="/place/"]')

    def search(self, keyword: str):

        self._urls = []
        self._seen_paths = set()

        url = f"https://www.google.com/maps/search/{quote(keyword)}"
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        self._dismiss_consent()
        self._cache_locators()

        try:
            self._feed.wait_for(state="visible", timeout=20000)
        except PlaywrightTimeoutError:
            self._place_links.first.wait_for(state="visible", timeout=15000)

    def _dismiss_consent(self):

        for sel in (
            'button:has-text("Accept all")',
            'button:has-text("Accept all cookies")',
            'button:has-text("I agree")',
            'button:has-text("Reject all")',
            'button[aria-label="Accept all"]',
        ):
            try:
                btn = self.page.locator(sel).first
                if btn.is_visible(timeout=400):
                    btn.click(timeout=1500)
                    return
            except Exception:
                continue

    def results(self):
        if self._place_links is None:
            self._place_links = self.page.locator('a[href*="/place/"]')
        return self._place_links

    def business_count(self):
        return len(self._urls)

    def _dom_place_count(self):

        if self.page.is_closed():
            return 0

        return self.page.evaluate(
            "() => document.querySelectorAll('a[href*=\"/place/\"]').length"
        )

    def _snapshot_urls(self):
        """Merge live feed links into self._urls (deduped by pathname)."""

        if self.page.is_closed():
            return len(self._urls)

        batch = self.page.evaluate(
            """() => {
                const seen = new Set();
                const out = [];
                for (const a of document.querySelectorAll('a[href*="/place/"]')) {
                    try {
                        const path = new URL(a.href).pathname;
                        if (!path.includes('/place/') || seen.has(path)) continue;
                        seen.add(path);
                        out.push([path, a.href]);
                    } catch (e) {}
                }
                return out;
            }"""
        )

        for path, href in batch:
            if path in self._seen_paths:
                continue
            self._seen_paths.add(path)
            self._urls.append(href)

        return len(self._urls)

    def load_more(self, target=100):

        if self._feed is None:
            self._cache_locators()

        count = self._snapshot_urls()
        print(f"Loaded: {count}")

        while count < target:

            if self.page.is_closed():
                break

            try:
                dom_before = self._dom_place_count()
                self._feed.evaluate("(e) => { e.scrollTop = e.scrollHeight; }")

                try:
                    self.page.wait_for_function(
                        "n => document.querySelectorAll('a[href*=\"/place/\"]').length > n",
                        arg=dom_before,
                        timeout=2000,
                    )
                except PlaywrightTimeoutError:
                    pass

                next_count = self._snapshot_urls()

                # Stop immediately when no new unique Place URLs appear
                if next_count <= count:
                    print("No more results.")
                    break

                count = next_count
                print(f"Loaded: {count}")

            except Exception as e:
                print(f"FAIL load_more: {e}")
                break

        return self._urls[:target]

    def collect_urls(self, limit=100):
        """Return deduplicated place URLs collected from the results feed."""

        if not self.page.is_closed():
            try:
                self._snapshot_urls()
            except Exception as e:
                print(f"FAIL collect_urls: {e}")

        return self._urls[:limit]

    def release(self):
        """Drop cached DOM state after URL collection."""

        self._feed = None
        self._place_links = None
        self._urls = []
        self._seen_paths.clear()

    def open_business(self, index):
        """Unused by the URL-driven flow — kept for compatibility."""

        try:
            cards = self.results()
            if index >= cards.count():
                return False
            cards.nth(index).click(timeout=3000)
            self.page.locator("h1").first.wait_for(state="visible", timeout=3000)
            return True
        except Exception as e:
            print(f"Open failed: {e}")
            return False

    def back_to_results(self):
        """Unused by the URL-driven flow — kept for compatibility."""

        try:
            self.page.locator('button[aria-label="Back"]').first.click(timeout=3000)
            if self._feed is None:
                self._cache_locators()
            self._feed.wait_for(state="visible", timeout=3000)
        except Exception as e:
            print(f"Back failed: {e}")
