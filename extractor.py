import re

from playwright.sync_api import Page

from models.business import Business


_ICON_RE = re.compile(r"[\ue000-\uf8ff]")
_SPACE_RE = re.compile(r"\s+")


def _clean_text(value: str) -> str:

    if not value:
        return ""

    value = _ICON_RE.sub("", value)
    return _SPACE_RE.sub(" ", value).strip()


class BusinessExtractor:

    _TYPE_KEYWORDS = (
        "repair",
        "service",
        "auto",
        "mechanic",
        "garage",
        "european",
        "bmw",
        "transmission",
        "tire",
        "oil",
        "body",
    )

    def __init__(self, page: Page):
        self.page = page
        self._h1 = None
        self._keywords = list(self._TYPE_KEYWORDS)

    def _cache_locators(self):
        self._h1 = self.page.locator("h1").first

    def open_first_business(self):

        cards = self.page.locator('a[href*="/place/"]')
        cards.first.wait_for(state="visible", timeout=10000)
        cards.first.click()
        self._cache_locators()
        self._h1.wait_for(state="visible", timeout=10000)

    def extract(self):
        """Extract business fields from the current place page (after page.goto)."""

        business = Business()
        business.maps_url = self.page.url

        if self._h1 is None:
            self._cache_locators()

        try:
            self._h1.wait_for(state="visible", timeout=5000)
        except Exception:
            pass

        try:
            data = self.page.evaluate(
                """(keywords) => {
                    const clean = (el) => {
                        if (!el) return "";
                        return (el.innerText || "")
                            .replace(/[\\uE000-\\uF8FF]/g, "")
                            .replace(/\\s+/g, " ")
                            .trim();
                    };

                    let name = "";
                    const h1 = document.querySelector("h1");
                    if (h1) {
                        const t = (h1.innerText || "").trim();
                        if (t && t.toLowerCase() !== "results") name = t;
                    }

                    const website = document.querySelector('a[data-item-id="authority"]');
                    const phone = document.querySelector('button[data-item-id^="phone"]');
                    const address = document.querySelector('button[data-item-id="address"]');

                    let business_type = "Unknown";
                    const buttons = document.querySelectorAll("button[jsaction]");
                    for (let i = 0; i < Math.min(buttons.length, 50); i++) {
                        const text = (buttons[i].innerText || "").trim();
                        if (!text || text.length > 40) continue;
                        const lower = text.toLowerCase();
                        if (keywords.some((k) => lower.includes(k))) {
                            business_type = text;
                            break;
                        }
                    }

                    let is_open = true;
                    const statusEl = document.querySelector(
                        'div[aria-label*="Open"], div[aria-label*="Closed"]'
                    );
                    if (statusEl) {
                        const status = (statusEl.innerText || "").toLowerCase();
                        if (
                            status.includes("temporarily closed") ||
                            status.includes("permanently closed") ||
                            (status.includes("closed") && !status.includes("open"))
                        ) {
                            is_open = false;
                        }
                    }

                    return {
                        name,
                        website: website ? website.href : "",
                        phone: clean(phone),
                        address: clean(address),
                        business_type,
                        is_open,
                    };
                }""",
                self._keywords,
            )
        except Exception:
            data = {}

        business.name = _clean_text(data.get("name") or "")
        business.website = (data.get("website") or "").strip()
        business.phone = _clean_text(data.get("phone") or "")
        business.address = _clean_text(data.get("address") or "")
        business.business_type = data.get("business_type") or "Unknown"
        business.is_open = bool(data.get("is_open", True))

        if not business.name:
            try:
                title = self.page.title()
                if " - Google Maps" in title:
                    business.name = _clean_text(
                        title.replace(" - Google Maps", "")
                    )
            except Exception:
                pass

        return business
