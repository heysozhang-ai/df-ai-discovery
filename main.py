from browser import BrowserManager

from maps import GoogleMaps
from extractor import BusinessExtractor
from website_scraper import WebsiteScraper
from storage import Storage
from rule_engine import RuleEngine


def main():

    browser = BrowserManager(headless=False)

    # Google Maps 专用 Page
    page = browser.start()

    # 官网抓取专用 Page（独立）
    website_page = browser.new_page()

    storage = Storage()

    maps = GoogleMaps(page)

    maps.search("BMW repair Dallas")

    maps.load_more(100)

    extractor = BusinessExtractor(page)

    # 使用独立 Page 抓官网
    scraper = WebsiteScraper(website_page)

    total = min(maps.business_count(), 100)

    print(f"\nFound {total} businesses\n")

    for i in range(total):

        print(f"\n========== {i+1}/{total} ==========\n")

        try:

            if not maps.open_business(i):
                print("Open failed.")
                continue

            business = extractor.extract()

            if RuleEngine.should_skip(business):
                print("SKIP Dealer :", business.name)
                maps.back_to_results()
                continue

            if storage.exists(business.maps_url):
                print("SKIP Exists :", business.name)
                maps.back_to_results()
                continue

            business.email = scraper.find_email(
                business.website
            )

            RuleEngine.score(business)

            storage.save(business)

            print(business.to_dict())

            maps.back_to_results()

        except Exception as e:

            print(f"ERROR : {e}")

            try:
                maps.back_to_results()
            except:
                pass

            continue

    storage.close()

    input("\nFinished. Press ENTER to exit...")

    browser.close()


if __name__ == "__main__":
    main()
