import re
from urllib.parse import urljoin, urlparse

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


class WebsiteScraper:

    EMAIL_PATTERN = re.compile(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        re.IGNORECASE,
    )

    IGNORE = {
        "example@example.com",
        "your@email.com",
        "email@example.com",
    }

    INVALID_SUFFIX = (
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".svg",
        ".ico",
        ".css",
        ".js",
        ".woff",
        ".woff2",
        ".ttf",
        ".map",
    )

    NAV_TIMEOUT = 5000

    def __init__(self, page: Page):
        self.page = page
        self._email_by_domain = {}

    @staticmethod
    def _domain(url: str) -> str:

        try:
            host = urlparse(url).netloc.lower()
            if host.startswith("www."):
                host = host[4:]
            return host
        except Exception:
            return ""

    def _find_email_in_html(self, html: str):

        for email in self.EMAIL_PATTERN.findall(html):

            email = email.lower().strip()

            if email in self.IGNORE:
                continue

            if email.endswith(self.INVALID_SUFFIX):
                continue

            return email

        return ""

    def find_email(self, url: str):

        if not url:
            return ""

        domain = self._domain(url)

        if domain and domain in self._email_by_domain:
            return self._email_by_domain[domain]

        email = self._scrape_email(url)

        if domain:
            self._email_by_domain[domain] = email

        return email

    def _scrape_email(self, url: str) -> str:

        try:

            if self.page.is_closed():
                return ""

            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.NAV_TIMEOUT,
            )

            email = self._find_email_in_html(self.page.content())
            if email:
                return email

            contact_href = self.page.evaluate(
                """() => {
                    const wanted = new Set(["contact", "contact us", "contacts"]);
                    for (const a of document.querySelectorAll("a[href]")) {
                        const text = (a.innerText || "").trim().toLowerCase();
                        if (wanted.has(text)) return a.getAttribute("href");
                    }
                    return null;
                }"""
            )

            if not contact_href:
                return ""

            self.page.goto(
                urljoin(url, contact_href),
                wait_until="domcontentloaded",
                timeout=self.NAV_TIMEOUT,
            )

            return self._find_email_in_html(self.page.content())

        except PlaywrightTimeoutError:
            return ""
        except Exception:
            return ""
