from playwright.sync_api import sync_playwright
import requests
import os
from urllib.parse import urljoin, urlparse

def download_image(url, folder="images"):
    os.makedirs(folder, exist_ok=True)
    filename = os.path.basename(urlparse(url).path)
    if not filename:
        filename = f"image_{abs(hash(url))}.jpg"
    filepath = os.path.join(folder, filename)

    try:
        resp = requests.get(url, stream=True, timeout=10)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            print(f"Saved: {filepath}")
        else:
            print(f"Error {resp.status_code} downloading {url}")
    except Exception as e:
        print(f"Download error: {url} → {e}")

def download_first_n_images(start_url, n=10, folder="images"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(start_url, wait_until="networkidle")

        # Scroll to the bottom to prompt lazy-load
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)  # wait for images to load

        # Grab first N images
        img_elements = page.query_selector_all("img")
        count = 0
        for img in img_elements:
            if count >= n:
                break
            src = img.get_attribute("src") or img.get_attribute("data-src")
            if src:
                img_url = urljoin(page.url, src)
                print(f"[{count+1}/{n}] Found image: {img_url}")
                download_image(img_url, folder)
                count += 1

        browser.close()
        print(f"Finished downloading {count} images.")

if __name__ == "__main__":
    start_url = 'https://www.njmls.com/listings/index.cfm?zoomlevel=0&action=dsp.results&page=1&display=30&sortBy=newest&isFuzzy=false&location=&city=&state=&county=&zipcode=&radius=&proptype=%2C2&maxprice=&minprice=&beds=0&baths=0&dayssince=&newlistings=&pricechanged=&keywords=&mls_number=&garage=&basement=&fireplace=&pool=&laundry=&elevator=&fitnesscenter=&furnished=&shortterm=&dogsallowed=&catsallowed=&earliestdate=&latestdate=&yearBuilt=&building=&officeID=&openhouse=&countysearch=false&ohdate=&style=&rerun=&rerundate=&searchname=&backtosearch=false&token=false&searchid=&searchcountid=&emailalert_yn=I&status=A&_=1757370140790&countysearch=false'

    #'https://www.njmls.com/listings/index.cfm?zoomlevel=0&action=dsp.results&page=1&display=30&sortBy=newest&isFuzzy=false&location=&city=&state=&county=&zipcode=&radius=&proptype=%2C2&maxprice=&minprice=&beds=0&baths=0&dayssince=&newlistings=&pricechanged=&keywords=&mls_number=&garage=&basement=&fireplace=&pool=&laundry=&elevator=&fitnesscenter=&furnished=&shortterm=&dogsallowed=&catsallowed=&earliestdate=&latestdate=&yearBuilt=&building=&officeID=&openhouse=&countysearch=false&ohdate=&style=&rerun=&rerundate=&searchname=&backtosearch=false&token=false&searchid=&searchcountid=&emailalert_yn=I&status=A&_=1757370140790&countysearch=false'
    
    
    
    #'https://www.njmls.com/listings/index.cfm?zoomlevel=0&action=dsp.results&page=1&display=30&sortBy=newest&isFuzzy=false&location=&city=&state=&county=&zipcode=&radius=&proptype=%2C1%2C2&maxprice=&minprice=&beds=0&baths=0&dayssince=&newlistings=&pricechanged=&keywords=&mls_number=&garage=&basement=&fireplace=&pool=&laundry=&elevator=&fitnesscenter=&furnished=&shortterm=&dogsallowed=&catsallowed=&earliestdate=&latestdate=&yearBuilt=&building=&officeID=&openhouse=true&countysearch=false&ohdate=&style=&rerun=&rerundate=&searchname=&backtosearch=false&token=false&searchid=&searchcountid=&emailalert_yn=I&status=A&_=1757370121375&countysearch=false'
    #"https://www.njmls.com/listings/index.cfm?action=dsp.results&proptype=1%2C2&status=A&mlsSearch=1&minprice=&maxprice="
    
    download_first_n_images(start_url, n=500, folder="njmls_images")
