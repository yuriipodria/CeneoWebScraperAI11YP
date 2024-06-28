from app import app
from app.modules.Scraper import Scraper
from app.modules.Product import Product
from flask import render_template, request, redirect, url_for, send_file
import requests
import os
import json
import pandas as pd
import numpy as np
from io import BytesIO
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')

@app.route('/')
@app.route('/index')
def index():
  return render_template("index.html")

@app.route('/extract', methods=['GET', 'POST'])
def extract():
  if request.method == 'POST':
    product_id = request.form.get('product_id')
    scraper = Scraper(product_id)
    scraper.scrape_opinions()

    if scraper.response_status_code != requests.codes['ok']:
      return render_template('extract.html', error = "Product does not exist")

    if scraper.opinions:
      scraper.save_opinions_to_json()

      product = Product(product_id, scraper.product_name, scraper.opinions)
      product.generate_charts()

      return redirect(url_for('product', product_id=product_id))

    return render_template('extract.html', error = "Product has no opinions")
  
  return render_template("extract.html")

@app.route('/products')
def products():
  products_list = []

  if os.path.exists("app/opinions"):
    for product_name in os.listdir("app/opinions"):
      with open(f"app/products/{product_name}", "r", encoding="UTF-8") as jf:
        product_info = json.load(jf)
        products_list.append(product_info)

  return render_template("products.html", products=products_list)

@app.route('/author')
def author():
  return render_template("author.html")

@app.route('/product/<product_id>')
def product(product_id):
  opinions = pd.read_json(f"app/opinions/{product_id}.json")
  return render_template("product.html", product_id=product_id, opinions=opinions.to_html(table_id="opinions"))

@app.route('/charts/<product_id>')
def charts(product_id):
  return render_template("charts.html", product_id=product_id)

@app.route('/download/json/<product_id>')
def download_json(product_id):
  opinions_file = f"opinions/{product_id}.json"
  return send_file(opinions_file, mimetype='text/json', download_name=f'{product_id}.json', as_attachment=True)

@app.route('/download/csv/<product_id>')
def download_csv(product_id):
  opinions_file = f"app/opinions/{product_id}.json"
  opinions_data = pd.read_json(opinions_file)
  opinions_data = pd.concat([opinions_data.drop(['content'], axis=1), opinions_data['content'].apply(pd.Series)], axis=1)
  response_stream = BytesIO()
  opinions_data.to_csv(response_stream, index=False)
  response_stream.seek(0)
  return send_file(response_stream, mimetype='text/csv', download_name=f'{product_id}.csv', as_attachment=True)

@app.route('/download/xlsx/<product_id>')
def download_xlsx(product_id):
  opinions_file = f"app/opinions/{product_id}.json"
  opinions_data = pd.read_json(opinions_file)
  buffer = BytesIO()
  with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
    opinions_data.to_excel(writer, index=False)
  buffer.seek(0)
  return send_file(buffer, mimetype='text/xlsx', download_name=f'{product_id}.xlsx', as_attachment=True)
