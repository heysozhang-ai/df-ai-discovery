import re
from playwright.sync_api import Page


class WebsiteScraper:

    def __init__(self, page: Page):
        self.page = page

    def find_email(self, url: str):

        if not url:
            return ""

        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
        except:
            return ""

        html = self.page.content()

        emails = re.findall(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            html,
            flags=re.IGNORECASE,
        )

        ignore = {
            "example@example.com",
            "your@email.com",
            "email@example.com",
        }

        for email in emails:
            email = email.lower()

            if email not in ignore:
                return email

        return ""
