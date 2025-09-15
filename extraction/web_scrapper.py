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
    self.price = price
    self.rooms = rooms
    self.basement = basement
    self.garage = garage
    self.category = category
    self.list_date = list_date
    self.property_tax = property_tax
    self.description = description
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
      for img in soup.select("img.newimg"):
          src = img.get("src") or img.get("data-src")
          if src:
              if src[:6] != 'https:':
                  src = 'https:' + src
              self.image_urls.append(src)
      return self.image_urls
    
    except Exception as e:
       print(f"Could not get information from listing url...Error {e}")
       return []


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

  def parse_description(self):
      data = self.scrape_description()
      self.address = data.get("Address")
      self.town = data.get("Town")
      self.beds = self._to_int(data.get("bedrooms"))
      self.full_baths = self._to_int(data.get("full baths"))
      self.half_baths = self._to_int(data.get("half baths"))
      self.price = self._parse_price(data.get("Current Price"))
      self.rooms = self._to_int(data.get("Rooms"))
      self.basement = data.get("basement")
      self.garage = data.get("garage")
      self.category = data.get("category")
      self.list_date = data.get("list date")
      self.property_tax = self._parse_price(data.get("taxes"))
      return data
  
  def _parse_price(self, val):
    if not val:
        return None
    return int(val.replace("$", "").replace(",", "").strip())

  def _to_int(self, val):
      try:
          return int(val)
      except (TypeError, ValueError):
          return None

if __name__ == '__main__':

  url = 'https://www.njmls.com/listings/index.cfm?action=dsp.info&mlsnum=25032829&openhouse=true&dayssince=15&countysearch=false'
  property_check = Property(url)
  print(property_check.scrape_description())
  print(property_check.scrape_image_urls())