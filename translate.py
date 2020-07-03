#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time, os, re, sys, codecs
import pyperclip
import requests
from bs4 import BeautifulSoup
from lxml import html
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import ElementClickInterceptedException as ECIE
# removed in the updated version
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

program_start = time.time()

#スパイダー関数を作成して、100個のリンクのリストを作成
def spider_top_100():
	top_100_url = "https://www.gutenberg.org/browse/scores/top"
	res = requests.get(top_100_url)
	html_text = res.text
	html.fromstring()


# book_url = "http://www.gutenberg.org/files/2500/2500-h/2500-h.htm"
book_url = "https://www.gutenberg.org/files/0/2/2-h/2-h.htm"

def get_text(url):
	res = requests.get(url)
	html_text = res.text
	res.close()
	return html_text

html_text = get_text(book_url)


#ファイル出力をUTF8に指定
# log = codecs.open('log.txt', 'a', 'utf-8')

#BeauifulSoupで解析
html_soup = BeautifulSoup(html_text, "html.parser")

#h1,h2,h3,pタグを抽出
paragraph_list_bs4 = html_soup.find_all(["h1", "h2", "h3", "p"]);



#文字列の前処理
def preprocessing(list):
	f_list = []
	b_list = []
	for paragraph in list:

		#タグを除去
		paragraph_without_tag = paragraph.text
		
		#改行をスペースに変換
		escaped_paragraph = re.sub("[\r\n]+", " ", paragraph_without_tag)

		#複数個のスペースを一個のスペースに変換
		final_paragraph = re.sub("  +", " ", escaped_paragraph)

		#冒頭がスペースなら削除する
		if final_paragraph[0] == " ":
			final_paragraph = final_paragraph[1:]

		#パラグラフがスペースだけの文字列ならリストから除外
		for character in final_paragraph:
			if character == ' ':
				continue
			else:
				f_list.append(final_paragraph)
				b_list.append(paragraph)
				break

	return f_list, b_list

#関数を実行
final_paragraph_list, before_list = preprocessing(paragraph_list_bs4)

print("final len {l}".format(l =len(final_paragraph_list)))
print("before len {l}".format(l =len(before_list)))

contem = "aiueo"
for i, list in enumerate(before_list):
	slist = str(list)
	if list.text not in slist:
		print(i)

	# print(slist.replace(list.text, contem))
# log = open('log.txt', 'a', encoding='utf-8')
# for i, list in enumerate(before_list):
# 	# print(list, file=log)
# 	if list.text is None:
# 		print(i)
# 		print(list)
# 		print(list.text)
# log.close()

#左のテキストエリアにコピペ
def copy_paste(input, xpath):
	pyperclip.copy(input)
	driver.find_element_by_xpath(xpath).send_keys(Keys.CONTROL, "v")

#ボタンまで移動
def slide_to(xpath):
	element = driver.find_element_by_xpath(xpath)
	actions = ActionChains(driver)
	actions.move_to_element(element).perform()

#JSでボタンをクリックして確実にコピー
def click_button_with_JS(script):
	click_counts = 0
	js_click_start = time.time()
	pyperclip.copy('')
	while (pyperclip.paste() == '') or ('[...]' in pyperclip.paste()):
		driver.execute_script(script)
		click_counts = click_counts + 1

		if time.time() - js_click_start > 30:
			print('this paragraph includes [...]')
			print(pyperclip.paste())
			break
	#インプットテキストエリアをクリアする
	driver.find_element_by_xpath(input_xpath).clear()

#文頭がスペースならスペース除去
def remove_top_space(string):
	if string[0] == " ":
		string = string[1:]
		return string
	else:
		return string

def open_putoff_cookie(url):
	driver.get(url)
	start = time.time()
	try:
		try:
			driver.find_element_by_xpath(cookie_button_xpath).click()
		except:
			time.sleep(3)
			driver.find_element_by_xpath(cookie_button_xpath).click()
			print('passed except clause')
		else:
			print('passed inner try clause')
	except:
		print('No cookie element found')

	# driver.find_element_by_xpath(language_button_xpath).click()
	# slide_to(japanese_button_xpath)
	# driver.find_element_by_xpath(japanese_button_xpath).click()	
	finish = time.time()
	elapsed_time = finish - start
	time_log = open('time.txt', 'a', encoding='utf-8')
	print("lounch time: {s}".format(s=elapsed_time), file=time_log)
	time_log.close()

input_xpath = '//*[@id="dl_translator"]/div[1]/div[3]/div[2]/div/textarea'
output_xpath = '//*[@id="dl_translator"]/div[1]/div[4]/div[3]/div[1]/textarea'
button_xpath = '//*[@id="dl_translator"]/div[1]/div[4]/div[3]/div[4]/div[1]/button'
#ブラウザを開いた時に現れるcookie取得を許可するポップアップのボタン
cookie_button_xpath = '//*[@id="dl_cookieBanner"]/div/div/div/span/div[2]/button[1]'
language_button_xpath = '//*[@id="dl_translator"]/div[1]/div[4]/div[1]/div[1]/div[1]/button'
japanese_button_xpath = '//*[@id="dl_translator"]/div[1]/div[4]/div[1]/div[1]/div[1]/div/button[@dl-lang="JA"]'


#deeplにアクセス
translator_url = "https://www.deepl.com/ja/translator"
driver = webdriver.Chrome()
driver.implicitly_wait(10)

open_putoff_cookie(translator_url)

# button_element = driver.find_element_by_xpath(button_xpath)
# actions = ActionChains(driver)

#copyボタンをクリックするjavascript
script_for_click = "document.querySelector('#dl_translator > div.lmt__sides_container > div.lmt__side_container.lmt__side_container--target > div.lmt__textarea_container > div.lmt__target_toolbar > div.lmt__target_toolbar__copy > button').click()"
        

#翻訳済みのパラグラフを格納するリスト
translated_list = []

#何回イテレーションを回したかのカウンター
counts = 0


log = open('log.txt', 'a', encoding='utf-8')

for paragraph in final_paragraph_list:
	
	#1回のイテレーションで何秒かかるかを測定
	paragraph_start = time.time()

	#5000字を越えたパラグラフが翻訳されたもの格納する文字列
	paragraph_over5000 = ""

	while len(paragraph) > 5000:
		#パラグラフを１文字ずつ精査して5000字目に一番近いピリオドの場所を探している。
		for i in range(5000):
			if paragraph[5000-i] == ".":
				period = 5000-i
				break

		# #5000字以内に文章を切り取ってクリップボードにコピーして左側に貼り付け
		copy_paste(paragraph[:period+1], input_xpath)
		# pyperclip.copy(paragraph[:period+1])
		# driver.find_element_by_xpath(input_xpath).send_keys(Keys.CONTROL, "v")

		#ボタンまで移動
		slide_to(button_xpath)
		# button_element = driver.find_element_by_xpath(button_xpath)
		# actions = ActionChains(driver)
		# actions.move_to_element(button_element).perform()

		#Javascriptを使った方法でボタンをクリックしてコピー
		click_button_with_JS(script_for_click)
		# click_counts = 0
		# click_start = time.time()
		# while (pyperclip.paste() == '') or ('[...]' in pyperclip.paste()):
		# 	driver.execute_script(script)
		# 	click_counts = click_counts + 1

		# 	if time.time() - click_start > 30:
		# 		print('this paragraph includes [...]')
		# 		break

		#ペーストされた日本語を変数に代入
		paragraph_over5000 = paragraph_over5000 + pyperclip.paste()

		#残りの部分を抽出
		paragraph = paragraph[period+1:]

		#文頭がスペースならスペース除去
		paragraph = remove_top_space(paragraph)
		# if paragraph[0] == " ":
		# 	paragraph = paragraph[1:]


	#テキストエリアにコピペ
	copy_paste(paragraph, input_xpath)
	
	#ボタンまで移動
	slide_to(button_xpath)

	#Javascriptを使った方法でボタンをクリックしてコピー
	click_button_with_JS(script_for_click)
	# click_counts = 0
	# click_start = time.time()
	# while (pyperclip.paste() == '') or ('[...]' in pyperclip.paste()):
		
	# 	driver.execute_script(script)
	# 	click_counts = click_counts + 1

	# 	if time.time() - click_start > 30:
	# 		print('this paragraph includes [...]')
	# 		break

	#ペースト
	if paragraph_over5000 != '':
		translated_paragraph = paragraph_over5000 + pyperclip.paste()
	else:
		translated_paragraph = pyperclip.paste()

	#ログファイルにペーストしたものを書き込む
	print(translated_paragraph, file=log)

	#翻訳済みのリストを作成
	translated_list.append(translated_paragraph)


	counts = counts + 1
	paragraph_finish = time.time()
	interval = paragraph_finish - paragraph_start

	time_log = open('time.txt', 'a', encoding='utf-8')
	print("{c}  : {i}".format(c=counts-1, i=interval), file=time_log)
	time_log.close()

	if counts % 5 == 0:
		cap = driver.desired_capabilities
		print(cap)
		cap.pop('proxy')
		print("driver has closed because iteration excess {s} times".format(s=counts))
		driver.start_session(cap)
		open_putoff_cookie(translator_url)

	# if interval > 5:
	# 	driver.refresh()
	# 	print("driver has refreshed because interval excess 5 seconds")


log.close()
driver.quit()
print("finished translating!")

#データベースに格納するデータ
title_bs4 = html_soup.find("h2")
book_title = title_bs4.text

author_bs4 = html_soup.find("h2")
book_author = author_bs4.text

book_body = ""
for x, y in zip(before_list, translated_list):
	x_str = str(x)
	xx = x_str.replace(x.text, y)
	book_body = book_body + xx


#conneting database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = 'sqlite:///' + os.path.join(basedir, 'db', 'gutenberg.sqlite3')

from app import Books, db
result = Books(url=book_url, title=book_title, author=book_author, body=book_body)
db.session.add(result)
db.session.commit()

print("database updated!")
total_time= time.time() - program_start

time_log = open('time.txt', 'a', encoding='utf-8')
print("total time {t}".format(t=total_time), file=time_log)
time_log.close()