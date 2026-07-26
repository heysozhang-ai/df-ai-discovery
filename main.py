from browser import BrowserManager

from maps import GoogleMaps

from extractor import BusinessExtractor

from website_scraper import WebsiteScraper

from storage import Storage

from rule_engine import RuleEngine

def main():

    browser = BrowserManager(headless=False)

    page = browser.start()

    storage = Storage()

    maps = GoogleMaps(page)

    maps.search("BMW repair Dallas")

    maps.load_more(100)

    extractor = BusinessExtractor(page)

    scraper = WebsiteScraper(page)

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

            business.email = scraper.find_email(business.website)

            RuleEngine.score(business)

            storage.save(business)

            print(business.to_dict())

            # ★ 保存以后必须返回列表

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
