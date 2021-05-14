import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, os, requests

#   Program that scrap data from money.pl, about historical prices of stocks
#   akcje.csv describe which stocks we want to scrap

def main():
	data = pd.read_csv("akcje.csv")
	interest = data["Walor"]
	url = 'https://www.money.pl/gielda/spolki-gpw/'
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	
	result = soup.find('div', class_='rt-tbody')
	stocks = result.find_all('a', class_ = 'sc-18yizqs-0 sUail')
	#   Finding all available stocks at the site
	#   Extracting only stocks which are in ./(data_files/)akcje.csv, data_files is optional
	
	extract_urls = []
	
	for stock in stocks:
		def check(a):
			for j in interest:
				#   checking if stock is "interesting" i.e. is in this file
				if a == j:
					return True
			return False
		if check(stock.text):
			tmp = stock['href']
			tmp = tmp[19:len(tmp) - 5]
			extract_urls.append(url + tmp + ',archiwum.html')
			#   extracting it's href
	
	driver = webdriver.Chrome()
	driver.implicitly_wait(5)
	#   Some stuff for drivers (second one says wait 5 seconds before error)
	
	#   extract_urls = extract_urls[13:]
	#   if something doesn't work (execution stopped in proccess)
	#   then just slice extract_urls, so as to not copy same data twice
	#   added counter for simplicity
	
	counter = 0
	
	for eurl in extract_urls:
		#   eurl stands for extracted url XD
		print(eurl, end = " ")
		
		
		AKCEPTUJE_button_xpath = '/html/body/div[3]/div/div[2]/div[3]/div/button[2]'
		OKRES_textbox_xpath = '/html/body/div[4]/div/div[9]/div/div[2]/div/main/div[2]/div[1]/div/div[3]/div/div[1]/div/div/div/div/input'
		POBIERZCSV_button_xpath = '/html/body/div[4]/div/div[9]/div/div[2]/div/main/div[2]/div[1]/div/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div[8]/div/div/div/div[2]/button[2]'
		DWNMENU_svg_xpath = '/html/body/div[4]/div/div[9]/div/div[2]/div/main/div[2]/div[1]/div/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div[8]/div/div/div'
		PAGETITLE_h1_xpath = '/html/body/div[4]/div/div[9]/div/div[2]/div/main/div[1]/div/div/h1'
		#   this one is pretty self-explaining, just web-scraping of useful paths
		
		driver.get(eurl)
		action = webdriver.ActionChains(driver)
		try:
			driver.find_element_by_xpath(AKCEPTUJE_button_xpath).click()
		except:
			print('no accept button', end = ' ')
		driver.execute_script("window.scrollBy(0, 200);")
		time.sleep(2)
		date_box = driver.find_element_by_xpath(OKRES_textbox_xpath)
		date_box.clear()
		date_box.send_keys('01.01.2000 - 13.05.2021')
		date_box.send_keys(Keys.ENTER)
		
		#   on website in this order:
			#   accept pop-up window with cookies
			#   scroll window
			#   specify end date and start date (current date)
			#   move cursor on download button
			#   from drop down menu, select 'download as csv'
			#   move file in your computer to data_files/XYZ.csv, where XYZ is stock short name, extracted from website
		
		dwnmenu = driver.find_element_by_xpath(DWNMENU_svg_xpath)
		action.move_to_element(dwnmenu)
		action.perform()
		
		dwn_button = driver.find_element_by_xpath(POBIERZCSV_button_xpath)
		
		dwn_button.click()
		stock_name = driver.find_element_by_xpath(PAGETITLE_h1_xpath)
		def ext_name(a):
			#   just extracts name in parenthesis
			first = 0
			for i in range(len(a)):
				if a[i] == '(':
					first = i
					break
			a = a[first + 1:len(a) - 1]
			return a
		stock_name_str = ext_name(stock_name.text)
		time.sleep(3)
		os.system('mv ~/Downloads/moneypl*.csv ./data_files/' + stock_name_str + '.csv')
		print(' Done: ' + str(counter))
		counter += 1
		
		#   break
	
	print("YOU MADE IT!!!")
	wait_for_user_input = input()

if __name__ == "__main__":
	main()
