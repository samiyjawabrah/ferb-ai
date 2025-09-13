import requests
from bs4 import BeautifulSoup
from pprint import pprint


# class Property:
   
#   def __init__(self, url, address=None, beds=None, full_baths=None, half_baths=None, sq_ft= None, description=None):

#     #Url is mandatory to scrap
#     self.url = url

#     #Basic listing information
#     self.address = address
#     self.beds = beds
#     self.full_baths = full_baths
#     self.half_baths = half_baths
#     self.sq_ft = sq_ft

#     #Data for Vision Model
#     self.image_urls = []

#     #Data for Rent Prediciton Model
#     self.data = {}


    


def requestor(url):

  headers = {"User-Agent": "Mozilla/5.0"}
  res = requests.get(url, headers=headers)
  soup = BeautifulSoup(res.text, "html.parser")
  return soup


url = 'https://www.njmls.com/listings/index.cfm?action=dsp.info&mlsnum=25032829&openhouse=true&dayssince=15&countysearch=false'

soup = requestor(url)
# Select only the property images inside the owl-stage
image_urls = []
for img in soup.select("img.newimg"):
    src = img.get("src") or img.get("data-src")
    if src:
        if src[:6] != 'https:':
            src = 'https:' + src
        image_urls.append(src)

pprint(image_urls)

data = {}
labels = soup.find_all("span", class_="prompt-semibold")

for label in labels:
  key = label.get_text(strip=True)

  value_tag = label.find_parent("p").find_next_sibling("p")
  if value_tag:
    value = value_tag.get_text(" ", strip=True)
    data[key] = value

pprint(data)