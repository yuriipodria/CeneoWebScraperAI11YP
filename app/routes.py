from app import app
from app import utils
import requests
import os
import json
from bs4 import BeautifulSoup
from flask import render_template, request, redirect, url_for

@app.route('/')
@app.route('/index')
def index():
  return render_template("index.html")

@app.route('/extract', methods=['GET', 'POST'])
def extract():
  if request.method == 'POST':
    product_id = request.form.get('product_id')
    url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
    response = requests.get(url)
    if response.status_code == requests.codes['ok']:
      page_dom = BeautifulSoup(response.text, "html.parser")

      try:
        opinions_count = page_dom.select("a.product-review__link > span")
      except AttributeError:
        opinions_count = 0

      if opinions_count:
        product_name = page_dom.select_one("h1").get_text().strip()
        url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
        all_opinions = []
        while(url):
            print(url)
            response = requests.get(url)
            page_dom = BeautifulSoup(response.text, "html.parser")
            opinions = page_dom.select("div.js_product-review")
            for opinion in opinions:
                single_opinion = {
                    key: utils.extract(opinion, *value) 
                        for key, value in utils.selectors.items()
                }
                for key, value in utils.transformations.items():
                    single_opinion[key] = value(single_opinion[key])
                all_opinions.append(single_opinion)
            try:
                url = "https://www.ceneo.pl"+utils.extract(page_dom, "a.pagination__next", "href")
            except TypeError:
                url = None
            if not os.path.exists("app/opinions"):
              os.mkdir("app/opinions")
              jf = open(f"app/opinions/{product_id}.json", "w", encoding="UTF-8")
              json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
              jf.close()
        return redirect(url_for('product', product_id = product_id))
      return render_template('extract.html', error = "Product has no opinions")
    return render_template('extract.html', error = "Product does not exist")
  return render_template("extract.html")

@app.route('/products')
def products():
  if os.path.exists("app\opinions"):
    products = [filename.split(".")[0] for filename in os.listdir("app\opinions")]
  else:
    products = []
  return render_template("products.html")

@app.route('/author')
def author():
  return render_template("author.html")

@app.route('/product/<product_id>')
def product(product_id):
  return render_template("product.html", product_id=product_id)
