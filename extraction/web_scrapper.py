import requests
from bs4 import BeautifulSoup
from pprint import pprint

class Property:
   
  def __init__(self, url, address=None, beds=None, full_baths=None, half_baths=None, town=None, sq_ft= None, price=None, rooms=None, basement=None, garage=None, category=None, list_date=None, property_tax=None, description=None):

    # {'MLS #': '25032829', 'Town': 'Springfield', 'Address': '20  Maple Avenue', 'Current Price': '$599,000', 'Rooms': '10', 'bedrooms': '4', 'full baths': '2', 'half baths': '0', 'basement': 'Full,Unfinished', 'garage': 'Detached,Park Space', 'list date': '09/12/2025', 'category': 'Multi-Family', 'taxes': '$10,542'}
    #Url is mandatory to scrap
    self.url = url

    #Basic listing information
    self.address = address
    self.town = town
    self.beds = beds
    self.full_baths = full_baths
    self.half_baths = half_baths
    self.sq_ft = sq_ft

    #Data for Vision Model
    self.image_urls = []

    #Data for Rent Prediciton Model
    self.data = {}


  def requestor(self, url):

    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    return soup

  def scrape_image_urls(self):
    try:
      soup = self.requestor(self.url)
      # Select only the property images inside the owl-stage
      image_urls = []
      for img in soup.select("img.newimg"):
          src = img.get("src") or img.get("data-src")
          if src:
              if src[:6] != 'https:':
                  src = 'https:' + src
              image_urls.append(src)
      return image_urls
    
    except Exception as e:
       return "Could not access listing url..."


  def scrape_description(self):
    soup = self.requestor(self.url)
    data = {}
    labels = soup.find_all("span", class_="prompt-semibold")

    for label in labels:
        key = label.get_text(strip=True).rstrip(":")
        parent = label.parent
        if parent:
            # Get all text in parent, then remove the key itself
            full_text = parent.get_text(" ", strip=True)
            value = full_text.replace(label.get_text(strip=True), "").strip(": ").strip()
            if value:
                data[key] = value
    return data


if __name__ == '__main__':

  url = 'https://www.njmls.com/listings/index.cfm?action=dsp.info&mlsnum=25032829&openhouse=true&dayssince=15&countysearch=false'
  property_check = Property(url)
  print(property_check.scrape_description())
  print(property_check.scrape_image_urls())