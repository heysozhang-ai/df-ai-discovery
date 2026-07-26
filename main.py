import sys

sys.stdout.reconfigure(line_buffering=True)

from browser import BrowserManager
from maps import GoogleMaps
from extractor import BusinessExtractor
from website_scraper import WebsiteScraper
from storage import Storage
from rule_engine import RuleEngine


DIRECTORY_DOMAINS = (
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "yelp.",
    "yellowpages.",
    "bbb.org",
    "mapquest.",
    "youtube.com",
    "x.com",
    "twitter.com",
)


def _scrapable_website(url: str) -> bool:

    if not url:
        return False

    website = url.lower()
    return not any(x in website for x in DIRECTORY_DOMAINS)


def main():

    browser = BrowserManager(headless=False)
    page = browser.start()
    website_page = browser.new_page(block_media=True)

    storage = Storage()
    maps = GoogleMaps(page)
    extractor = BusinessExtractor(page)
    scraper = WebsiteScraper(website_page)

    # Phase 1 — search, scroll, collect + dedupe place URLs
    maps.search("BMW repair Dallas")
    maps.load_more(100)
    urls = maps.collect_urls(100)
    maps.release()

    if not urls:
        print("FAIL: no place URLs")
        storage.close()
        browser.close()
        return

    print(f"Found {len(urls)} places")

    businesses = []

    # Phase 2 — direct place navigation
    for i, url in enumerate(urls):

        try:
            page = browser.ensure_page(page)
            extractor.page = page
            extractor._h1 = None

            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            business = extractor.extract()

            if not business.name:
                print(f"SKIP: no name ({url})")
                continue

            if RuleEngine.should_skip(business):
                print(f"SKIP: dealer — {business.name}")
                continue

            if storage.exists(business.maps_url):
                print(f"SKIP: already saved — {business.name}")
                continue

            print(
                f"Business Name: {business.name}\n"
                f"Website: {business.website}\n"
                f"Email: {business.email}\n"
                f"Phone: {business.phone}\n"
                f"Address: {business.address}\n"
                f"Rule Score: {business.rule_score}\n"
                f"Approved: {business.approved}\n"
                f"Status: {business.status}"
            )
            storage.save(business)
            businesses.append(business)

        except Exception as e:
            print(f"ERR maps [{i + 1}]: {e}")
            page = browser.ensure_page(page)
            extractor.page = page
            extractor._h1 = None
            continue

    # Free Maps page memory before website phase
    urls.clear()
    try:
        page.goto("about:blank", wait_until="domcontentloaded", timeout=5000)
    except Exception:
        pass

    # Phase 3 — website/email on second page
    print(f"Websites: {len(businesses)}")

    for i, business in enumerate(businesses):

        try:
            website_page = browser.ensure_page(website_page, block_media=True)
            scraper.page = website_page

            if not _scrapable_website(business.website):
                print(f"SKIP: no scrapable website — {business.name}")
                continue

            business.email = scraper.find_email(business.website)
            RuleEngine.score(business)
            storage.update(business)

        except Exception as e:
            print(f"ERR web [{i + 1}]: {e}")
            website_page = browser.ensure_page(website_page, block_media=True)
            scraper.page = website_page
            continue

    storage.close()
    businesses.clear()
    scraper._email_by_domain.clear()
    print("Finished.")

    if sys.stdin.isatty():
        input("Press ENTER to exit...")

    browser.close()


if __name__ == "__main__":
    main()
