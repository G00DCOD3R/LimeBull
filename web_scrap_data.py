import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, os, requests, sys

#   Program that scrap data from money.pl, about historical prices of stocks
#   akcje.csv describe which stocks we want to scrap

def main():
	data = pd.read_csv("akcje.csv")
	interest = data["Walor"]
	url = 'https://www.money.pl/gielda/spolki-gpw/'
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	running_mode = 'MANUAL'
	if len(sys.argv) > 1:
		running_mode = 'AUTOMATED'
	print("current mode is " + str(running_mode))
	
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
	driver.implicitly_wait(6)
	#   Some stuff for drivers (second one says wait 6 seconds before error)
	
	
	latest_completed_download = -1
	if running_mode == 'AUTOMATED':
		tmp_file = open('TEMP_web_scrap_latest', 'r')
		latest_completed_download = int(tmp_file.readlines()[0])
		tmp_file.close()
	counter = latest_completed_download + 1
	
	extract_urls = extract_urls[counter:]
	#   print(extract_urls)
	#   if something doesn't work (execution stopped in proccess)
	#   then just slice extract_urls, so as to not copy same data twice
	#   added counter for simplicity
	#   by default latest_complete is set as -1, so as not to interfere with downloading process
	
	for eurl in extract_urls:
		#   eurl stands for extracted url XD
		print(eurl, end = " ")
		
		
		#   don't forget to update those paths, when website changes ;) 
		AKCEPTUJE_button_xpath = '/html/body/div[3]/div/div[2]/div[3]/div/button[2]'
		OKRES_textbox_xpath = '/html/body/div[5]/div/div[10]/div/div[2]/div/main/div[2]/div[1]/div/div[3]/div/div[1]/div/div/div/div/input'
		POBIERZCSV_button_xpath = '/html/body/div[5]/div/div[10]/div/div[2]/div/main/div[2]/div[1]/div/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div[8]/div/div/div/div[2]/button[2]'
		DWNMENU_svg_xpath = '/html/body/div[5]/div/div[10]/div/div[2]/div/main/div[2]/div[1]/div/div[3]/div/div[2]/div/div/div[1]/div[1]/div/div[8]/div/div/div/div[1]'
		PAGETITLE_h1_xpath = '/html/body/div[5]/div/div[10]/div/div[2]/div/main/div[1]/div/div/h1'
		YETANOTHERACCEPT_button_xpath = '/html/body/div[8]/div[5]'
		#   this one is pretty self-explaining, just web-scraping of useful paths
		
		driver.get(eurl)
		action = webdriver.ActionChains(driver)
		try:
			driver.find_element_by_xpath(AKCEPTUJE_button_xpath).click()
			driver.find_element_by_xpath(YETANOTHERACCEPT_button_xpath).click()
		except:
			print('no accept button', end = ' ')
		driver.execute_script("window.scrollBy(0, 200);")
		date_box = driver.find_element_by_xpath(OKRES_textbox_xpath)
		date_box.clear()
		date_box.send_keys('01.01.2000 - 17.04.2022')
		
		date_box.send_keys(Keys.ENTER)
		
		#   on website in this order:
			#   accept all pop-up windows with cookies
			#   scroll window
			#   specify end date and start date (current date)
			#   move cursor on download button
			#   from drop down menu, select 'download as csv'
			#   move file in your computer to data_files/XYZ.csv, where XYZ is stock short name, extracted from website
		
		time.sleep(3)
		dwnmenu = driver.find_element_by_xpath(DWNMENU_svg_xpath)
		action.move_to_element(dwnmenu)
		action.perform()
		
		dwn_button = driver.find_element_by_xpath(POBIERZCSV_button_xpath)
		
		def is_downloaded():
			path = r'/home/tymon/Downloads'
			#   os.chdir(path)
			files = os.listdir(path)
			for f in files:
				if 'moneypl' in f:
					return True
			return False
		
		if is_downloaded():
			if running_mode == 'MANUAL':
				print('\n\nYou already have some moneypl file in your download directory!\nPlease remove it before continuing\n\n')
				raise('File exists')
			else:
				os.system('rm ~/Downloads/moneypl*')
		
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
		
		#   downloading process
		
		

		seconds_passed = 0
		while seconds_passed <= 20:
			time.sleep(1)
			seconds_passed += 1
			if is_downloaded():
				break
		if not is_downloaded():
			raise('Downloading Failed')
		
		os.system('mv ~/Downloads/moneypl*.csv ./data_files/' + stock_name_str + '.csv')
		print(' Done: ' + str(counter))
		
		if running_mode == 'AUTOMATED':
			tmp_file = open('TEMP_web_scrap_latest', 'w')
			tmp_file.write(str(counter) + "\n")
			tmp_file.close()
			
		counter += 1
		
		#   break
	
	if running_mode == 'AUTOMATED':
		with open('TEMP_web_scrap_latest', 'w') as tmp_file:
			tmp_file.write("Done\n")
	else:
		print("YOU MADE IT!!!")
		wait_for_user_input = input()

if __name__ == "__main__":
	main()
