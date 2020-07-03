import os, requests, urllib
from bs4 import BeautifulSoup
from lxml import html

domain = "https://www.gutenberg.org"
top_100_url = "https://www.gutenberg.org/browse/scores/top"

def spider_bs4(url):
	res = requests.get(url)
	html_text = res.text
	html_bs4 = BeautifulSoup(res.text, 'html.parser')
	html_bs4_a = html_bs4.find_all('a')
	l = []
	for a in html_bs4_a:
		abspath = str(a.get("href"))
		if abspath[0:7] == "http://" or "https:/":
			abs_url = abspath
		else:
			abs_url = domain + abspath
		l.append(abs_url)

	return l

result_list = spider_bs4(top_100_url)

for url in result_list:
	print(url)

#スパイダー関数を作成して、100個のリンクのリストを作成
def spider_lxml(url):
	res = requests.get(url)
	html_text = res.text
	dom = html.fromstring(html_text)
	hatena = dom.xpath('string(/html/body/div[2]/div[3]/ol[1])')
	return hatena
