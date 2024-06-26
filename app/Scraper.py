import requests
import json
from app.Opinion import Opinion
from bs4 import BeautifulSoup
from app import utils

class Scraper:
  def __init__(self, product_id):
    self.product_id = product_id
    self.url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
    self.opinions = []

  def scrape_opinions(self):
    response = requests.get(self.url)
    self.response_status_code = response.status_code

    if response.status_code == requests.codes['ok']:
      page_dom = BeautifulSoup(response.text, "html.parser")
      self.product_name = page_dom.select_one("h1").get_text().strip()

      try:
        opinions_count = page_dom.select_one("a.product-review__link > span").get_text().strip()
      except AttributeError:
        opinions_count = 0

      if opinions_count:
        while self.url:
          response = requests.get(self.url)
          page_dom = BeautifulSoup(response.text, "html.parser")
          opinions = page_dom.select("div.js_product-review")
          for opinion in opinions:
            single_opinion = {
              key: utils.extract(opinion, *value)
              for key, value in utils.selectors.items()
            }
            for key, value in utils.transformations.items():
              single_opinion[key] = value(single_opinion[key])
            self.opinions.append(Opinion(**single_opinion))
          try:
            self.url = "https://www.ceneo.pl" + utils.extract(page_dom, "a.pagination__next", "href")
          except TypeError:
            self.url = None

  def save_opinions_to_json(self):
    with open(f"app/opinions/{self.product_id}.json", "w", encoding="UTF-8") as jf:
      json.dump([opinion.to_dict() for opinion in self.opinions], jf, indent=4, ensure_ascii=False)
