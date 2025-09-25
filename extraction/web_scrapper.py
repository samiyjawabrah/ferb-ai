import requests
from bs4 import BeautifulSoup
from pprint import pprint
import regex as re

class Property:
   
  def __init__(self, mls_id=None, address=None, beds=None, full_baths=None, half_baths=None, town=None, sq_ft= None, price=None, rooms=None, basement=None, garage=None, category=None, list_date=None, property_tax=None, description=None, image_urls=None, units=None, bathrooms=None, cooling=None, heating=None, lifestyle=None, parking=None, exterior=None, laundry=None, lot_description=None, utilities=None, year_built=None):

    # {'MLS #': '25032829', 'Town': 'Springfield', 'Address': '20  Maple Avenue', 'Current Price': '$599,000', 'Rooms': '10', 'bedrooms': '4', 'full baths': '2', 'half baths': '0', 'basement': 'Full,Unfinished', 'garage': 'Detached,Park Space', 'list date': '09/12/2025', 'category': 'Multi-Family', 'taxes': '$10,542'}
    #Url is mandatory to scrap
    self.mls_id = mls_id
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
    self.units = units
    self.bathrooms = bathrooms
    self.cooling = cooling
    self.heating = heating
    self.lifestyle = lifestyle
    self.parking = parking
    self.exterior = exterior
    self.laundry = laundry
    self.lot_description = lot_description
    self.utilities = utilities
    self.year_built = year_built
    #Data for Vision Model
    self.image_urls = image_urls or []
    #Data for Rent Prediciton Model

    def __repr__(self):
       return f"Property: {self.address}, {self.town} listed at ${self.price}"

class PropertyScraper:
  def __init__(self, url):
     self.url = url
    
  def requestor(self):

    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(self.url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    return soup

  def scrape_image_urls(self):
    try:
      soup = self.requestor()
      # Select only the property images inside the owl-stage
      seen = set()
      for img in soup.select("img.newimg"):
          src = img.get("src") or img.get("data-src")
          if src:
              if src[:6] != 'https:':
                src = 'https:' + src
              if src not in seen:
                seen.add(src)
      return list(seen)
    
    except Exception as e:
       print(f"Could not get information from listing url...Error: {e}.")
       return []


  def scrape_description(self):
    try:
      soup = self.requestor()
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

      remarks_header = soup.find("h4", string=lambda t: t and "Property Remarks" in t)
      if remarks_header:
          desc_tag = remarks_header.find_next("p", class_="mb-0 text-break")
          if desc_tag:
              description = desc_tag.get_text(" ", strip=True)
              if description:
                  data["description"] = description

                  sq_ft = re.findall(r"([\d,]{3,7})\s*(sq\.?\s*ft|square\s*feet)", description, flags=re.I)
                  if sq_ft:
                    
                    data['sq_ft'] = int(sq_ft[0][0].replace(",",""))

                  units = re.search(r"(\d+)\s+units?", description, flags=re.I)
                  if units:
                      data['units'] = int(units.group(1))


      features_section = soup.find("div", id="pfeatures")
      if features_section:
          # print(features_section)
          feature_labels = features_section.find_all("span", class_="prompt-semibold")
          for f_label in feature_labels:
              f_key = f_label.get_text(strip=True)
              parent = f_label.find_parent("p")
              if parent:
                  next_p = parent.find_next_sibling("p")
                  if next_p:
                      f_value = " ".join(next_p.stripped_strings)
                      if f_value:
                          data[f_key] = f_value

      print(data)
      return data
    except Exception as e:
       print(f"Could not get information from listing url...Error {e}")
       return {}
       

  #Add the Property class to be added here and add the information accordingly.
  def parse_property(self):
      data = self.scrape_description()
      images = self.scrape_image_urls()

      return Property(
          mls_id=data.get("MLS #"),
          address=data.get("Address"),
          town=data.get("Town"),
          price=self._parse_price(data.get("Current Price")),
          rooms=self._to_int(data.get("Rooms")),
          beds=self._to_int(data.get("bedrooms")),
          full_baths=self._to_int(data.get("full baths")),
          half_baths=self._to_int(data.get("half baths")),
          basement=data.get("basement"),
          garage=data.get("garage"),
          category=data.get("category"),
          list_date=data.get("list date"),
          property_tax=self._parse_price(data.get("taxes")),
          description=data.get("description"),
          image_urls=images,
          sq_ft=data.get("sq_ft"),
          units=data.get("units"),
          bathrooms= (self._to_int(data.get('full baths')) or 0) + (self._to_int(data.get('half baths')) or 0),
          cooling=data.get("Cooling"),
          heating=data.get("Heat/Cool"),
          lifestyle=data.get("Lifestyle"),
          parking=data.get("Parking"),
          exterior=data.get("Exterior"),
          laundry=data.get("Laundry"),
          lot_description=data.get("Lot Description"),
          utilities=data.get("Utilities"),
          year_built=data.get("Year Built"),)
  
  def _parse_price(self, val):
      if not val:
          return None
      try:
          return int(val.replace("$", "").replace(",", "").strip())
      except ValueError:
          return None


  def _to_int(self, val):
      try:
          return int(val)
      except (TypeError, ValueError):
          return None

if __name__ == '__main__':

  # url = 'https://www.njmls.com/listings/index.cfm?action=dsp.info&mlsnum=25032829&openhouse=true&dayssince=15&countysearch=false'
  url = 'https://www.njmls.com/listings/index.cfm?action=dsp.info&mlsnum=25031920&getBack=home&proptype=1%2C2%2C3&openhouse='
  scraper = PropertyScraper(url)
  prop = scraper.parse_property()
  print(prop)
  pprint(prop.__dict__)