# coding=utf-8

import scrapy
import re
from bs4 import BeautifulSoup
from scrapy.http import Request
import os
import time
import threading
import requests
from scrapy.utils.response import get_base_url

DIR_PATH = "/home/hy/spider"
HEADERS = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': "http://www.mmjpg.com"
}
lock = threading.Lock()

class H_animateSpider(scrapy.Spider):
	name = 'H_animate'
	start_urls = ["http://www.mmjpg.com/mm/1"]
	headers = {
		'X-Requested-With': 'XMLHttpRequest',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
					  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
		'Referer': "http://www.mmjpg.com"
	}


	#def start_requests(self):
	#	print start_urls
	#	yield Request(start_url, self.parse)
	def make_dir(self, folder_name):
		path = os.path.join(DIR_PATH, folder_name)
		if not os.path.exists(path):
			os.makedirs(path)
			print(path)
			os.chdir(path)
			return True
		print("Folder has existed!")
		return False

	def save_pic(self, pic_src, pic_cnt):
		"""
        将图片下载到本地文件夹
        """
		try:
			img = requests.get(pic_src, headers=HEADERS, timeout=10)
			img_name = "pic_cnt_{}.jpg".format(pic_cnt + 1)
			with open(img_name, 'ab') as f:
				f.write(img.content)
				print(img_name)
		except Exception as e:
			print(e)

	def hasNumber(self, inputString):
		#print "3333333333333333333"
		#print inputString
		#print "%r" % (bool(re.search(r'\d', inputString)))
		return bool(re.search(r'\d', inputString))

	def has2Number(self, inputString):
		#print "4444444444444444"
		#print "%r" % (bool(re.search(r'\d/\d', inputString)))
		return bool(re.search(r'\d/\d', inputString))

	def startWithmm(self, inputString):
		return inputString.startswith("/mm")

	def parse(self, response):
		print ("Begin the crawler")
		#print response.text
		r = response.text
		#folder_name = 'test_for_animate'
		#folder_name = BeautifulSoup(r, 'lxml').find('h2').text.encode('ISO-8859-1').decode('utf-8')
		folder_name = BeautifulSoup(r, 'lxml').find('h2').text
		print folder_name
		base_url = get_base_url(response)
		#self.make_dir(folder_name)
		#max_count = BeautifulSoup(r, 'lxml').find('div', class_='page').find_all('a')[-2].get_text()
		with lock:
			if self.make_dir(folder_name):
				# 套图张数
				max_count = BeautifulSoup(r, 'lxml').find('div', class_='page').find_all('a')[-2].get_text()
				print max_count
				print "max_countmax_countmax_countmax_countmax_countmax_countmax_countmax_countmax_count"
				# max_count = 2
				# 套图页面
				# url="http://www.mmjpg.com/mm/1"

				page_urls = [base_url + "/" + str(i) for i in range(1, int(max_count) + 1)]
				# 图片地址
				print page_urls
				img_urls = []
				for index, page_url in enumerate(page_urls):
					result = requests.get(page_url, headers=HEADERS, timeout=10).text
					# 最后一张图片没有a标签直接就是img所以分开解析
					if index + 1 < len(page_urls):
						img_url = \
							BeautifulSoup(result, 'lxml').find('div', class_='content').find(
								'a').img['src']
						print img_url
						img_urls.append(img_url)
					else:
						img_url = \
							BeautifulSoup(result, 'lxml').find('div', class_='content').find('img')[
								'src']
						print img_url
						img_urls.append(img_url)
				# print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
				for cnt, url in enumerate(img_urls):
					# print "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
					self.save_pic(url, cnt)
		sel = scrapy.Selector(response)
		links_in_page = sel.xpath('//a[@href]')
		for link in links_in_page:
			url =  str(link.re('href="(.*?)"')[0])
			print url
			#print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
			#if url:
			#	if not url.startswith('http://m.'):
			#		yield scrapy.Request(url, callback=self.parse)
			#print url


			if url:
				print url
				if not url.startswith('http://m.'):
					if self.hasNumber(url):
						if not self.has2Number(url):
							if not self.startWithmm(url):
								yield scrapy.Request(url, callback=self.parse)
			#print url
