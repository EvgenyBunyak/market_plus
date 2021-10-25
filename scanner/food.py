from bs4 import BeautifulSoup
from datetime import datetime
import json
import multiprocessing as mp
import os
import requests
from requests_html import HTMLSession

URL_HOME = 'https://www.perekrestok.ru'

def get_html(url):
	print('Get HTML ...')
	print(url)

	r = requests.get(url)
	if r.status_code == 200:
		print('Ok')
	else:
		print(r.status_code)
	return r.text

def render_html(url):
	print('Render HTML ...')
	print(url)

	session = HTMLSession()
	r = session.get(url)
	r.html.render()

	if r.status_code == 200:
		print('Ok')
	else:
		print(r.status_code)
	return r.html.html

def parse_products(url):
	soup = BeautifulSoup(render_html(url), 'html.parser')

	groups = soup.find_all('div', {'class': 'catalog-content-group__list'})

	for g in groups:
		items = g.find_all('div', {'class': 'product-card__content'})
		for i in items:
			title = i.find('div', {'class': 'product-card__title'}).text
			price = i.find('div', {'class': 'price-new'}).text
			price_old = i.find('div', {'class': 'price-old'})
			if price_old is not None:
				price_old = price_old.text
			print(title, price, price_old)

def parse_types(product):
	soup = BeautifulSoup(render_html(product['url']), 'html.parser')
	html_types = soup.find_all('h2', {'class': 'catalog-content-group__title'})

	product['types'] = [t.text for t in html_types if t.text != 'Рекомендуем']

def parse_catalog():
	catalog = []
	manager = mp.Manager()

	soup = BeautifulSoup(get_html(URL_HOME + '/cat'), 'html.parser')
	html_categories = soup.find_all('div', {'class': 'category-filter-item__content'})

	for c in html_categories:
		html_products = c.find_all('a')
		for p in html_products:

			#if p.text not in ['Молоко', 'Сыр']:
			#	continue

			product = manager.dict()
			product['name'] = p.text
			product['url'] = URL_HOME + p['href']

			catalog.append(product)

	pool = mp.Pool(processes = 8)
	pool.map(parse_types, catalog)

	for product in catalog:
		print(product)

def main():
	parse_catalog()

main()
