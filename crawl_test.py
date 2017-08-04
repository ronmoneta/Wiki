# -*- coding: utf-8 -*-

import urlparse
import urllib
import urllib2
import itertools
import os
import imghdr
import time
import codecs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from PIL import Image

URL = "http://www.zionistarchives.org.il/"
PARSER = 'html.parser'
PIC_LOCAL_LINK = r'C:\Users\user\Documents\Crawler\{0}.jpg'
DEBUG_FILE = r"C:\Users\user\Documents\Crawler\names.txt"
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Language': 'en-US,en;q=0.8',
       #'Accept-Encoding': 'gzip',
       'Upgrade-Insecure-Requests': '1',
       'Connection': 'keep-alive'}

def crawler(url):
	urls = [url]
	visited = [url]
	link_list = []
	imgs = []
	while len(urls) > 0:
		try:
			#browser,results = parse_js(urls[0])
			#htmltext = browser.page_source
			htmltext = connect(urls[0])
			soup = BeautifulSoup(htmltext, PARSER)
			print urls[0]
			urls.pop(0)
			for tag in soup.findAll('a',href=True):
				tag['href'] = urlparse.urljoin(url,tag['href'])
				if url in tag['href'] and tag['href'] not in visited:
					urls.append(tag['href'])
					visited.append(tag['href'])
			#for link in results.find_elements_by_class_name('gsa-click-link'):
				#link_list.append(link.get_attribute("href"))
			#urls = urls + link_list
			urls = list(set(urls))
			imgs = imgs + get_pics(soup)
		except:
			print "nooop!!!!!!"
			urls.pop(0)
	imgs = list(set(imgs))
	img_handler(imgs,url)
	#browser.quit()

def img_handler(imgs,url):
	#Recives list of imgs and the relevant url. try to download the imgs and save them locally.
	names = ''
	for img in imgs:
		if url not in img and 'http' not in img:
			img = url + img
		if not 'googleads' in img:   #('rgb' or 'gif' or 'pbm' or 'pgm' or 'ppm' or 'tiff' or 'rast' or 'xbm' or 'jpeg' or 'jpg' or 'bmp' or 'png') and
			file_name = img.split('/')[-1]
			if len(file_name.split('.')[-1]) > 3 and not (file_name.split('.')[-1] == ('tiff' or 'jpeg')): 
			#if the img for some reason has words afer the format,remove them.
				file_name = file_name.split('.')[-1][:3]
			if file_name == '':
				file_name = "not_real_name.jpg" #temp name for "not" pictures
			print img.encode('utf-8')
			#coded_file_name = file_name.encode('utf-8')
			coded_file_name = codecs.encode(file_name,'cp1255')
			try:
				download_pic(img, PIC_LOCAL_LINK.format(coded_file_name))
			except UnicodeEncodeError:
				coded_file_name = codecs.encode(file_name,'utf-8')
			except:
				names += coded_file_name + ' , '
				print "The Website has a problem with the picture. Check names.txt"
	with open (DEBUG_FILE,'wb') as f:
		f.write(names)

def RateLimited(maxPerSecond):
	#Limits the amount of requests per seconds.
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate

#@RateLimited(0.6)
def connect(url):
	#Recives urls. connects to the website and returns the pagesource.
	req = urllib2.Request(url, headers=HEADER)
	#req.add_header('User-agent', 'Mozilla 5.10')
	#req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
	res = urllib2.urlopen(req)
	htmltext = res.read()
	return htmltext

def get_pics(soup):
	#Recives souped text, finds all the imgs in it.
	imgs = []
	for tag in soup.findAll('img',src=True):
		img_link = tag['src']
		imgs.append(img_link) 
	imgs = list(set(imgs))
	return imgs

def download_pic(url,path):
	#Recives the wanted pic's url, and if it passes the critirea, saves it to path.
	urllib.urlretrieve(url.encode('utf-8'),path)
	if check_size(path) == False:
		os.remove(path)
		print "was removed!"

def check_size(pic_path):
	#Recives pic_path, checks if their size is big enough by defenition.
	if imghdr.what(pic_path) == None: #Checks that the downloaded file was indeed a picture.
		print 'Not an Image!'
		return False
	image = Image.open(pic_path)
	image_height = image.height
	image_width = image.width
	image_size = get_file_size(pic_path)
	if image_height > 500 and image_width > 500 and image_size > 150000:
		return True
	else:
		print 'bad pic size: {0}, and file size: {1}'.format(image.size,image_size/1000)
		return False

def get_file_size(path):
	#Returns file's size in Bytes
	statinfo = os.stat(path)
	return statinfo.st_size

def parse_js(url):
	#Recives webpage. parses it and returns it as an HTML.
	browser = webdriver.Chrome()
	browser.get(url)
	wait = WebDriverWait(browser, 60)
	results = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'search-result')))
	return browser, results

def main():
	crawler(URL)

if __name__ == "__main__":
	main()

#For the State Archive: Why does the JS returns only the first article/link? make JS part and HTML part work together.