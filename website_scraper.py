import re
from urllib.parse import urljoin

from playwright.sync_api import Page


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

    def __init__(self, page: Page):
        self.page = page

    def _find_email_in_html(self, html: str):

        emails = self.EMAIL_PATTERN.findall(html)

        for email in emails:

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

        try:

            if self.page.is_closed():
                return ""

            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=8000,
            )

            email = self._find_email_in_html(
                self.page.content()
            )

            if email:
                return email

            links = self.page.locator("a")

            count = min(links.count(), 30)

            for i in range(count):

                try:

                    link = links.nth(i)

                    text = link.inner_text().strip().lower()

                    if text not in {
                        "contact",
                        "contact us",
                        "contacts",
                    }:
                        continue

                    href = link.get_attribute("href")

                    if not href:
                        continue

                    contact_url = urljoin(url, href)

                    self.page.goto(
                        contact_url,
                        wait_until="domcontentloaded",
                        timeout=8000,
                    )

                    email = self._find_email_in_html(
                        self.page.content()
                    )

                    if email:
                        return email

                    break

                except:
                    continue

        except:
            return ""

        return ""
