from bs4 import BeautifulSoup
import pandas as pd
import datetime, os, requests

def form(S):
	s = list(S)
	for lf in range(len(s)):
		if s[lf] != ' ' and s[lf] != '	' and s[lf] != '\n':
			s = s[lf:]
			break
	for rg in range(len(s)-1, -1, -1):
		if s[rg] != ' ' and s[rg] != '	' and s[rg] != '\n':
			s = s[:rg+1]
			break
	for i in range(len(s)):
		if s[i] == ",":
			s[i] = "."
	return ''.join(s)

def scrap_data(date):
	url = 'https://www.gpw.pl/archiwum-notowan-full?type=10&instrument=&date=' + date
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	result = soup.find('section', class_ = 'mainContainer padding-left-20 padding-right-20 padding-bottom-20 quotations-archive')
	row_list = result.find_all('tr')
	
	if len(row_list) == 0:
		return None
	
	df = []

	for i in row_list[0]:
		if i.text != '\n':
			df.append((form(i.text), []))
		
	for row in row_list[1:]:
		i = 0
		for val in row:
			if val.text != '\n':
				df[i][1].append(form(val.text))
				i += 1
	
	temp_dict = {key: value for (key, value) in df}
	res = pd.DataFrame(temp_dict)
	return res

def main():
	
	print("updating script:")
	print("do you want to update only today's data? [y/n]")
	
	def yes_no():
		user_option = input()
		if user_option[0] == 'n' or user_option[0] == 'N':	
			return False
		elif user_option[0] == 'y' or user_option[0] == 'Y':
			return True
	
	date = ""
	if yes_no():
		date = datetime.datetime.now().strftime("%d-%m-%Y")
	else:
		print("\nusing checking_data.py after updating is highly recomended,\nsince you can double some information\nthus making datasets invalid\n")
		print("Please specify data in format (d-m-Y)")
		date = input()
		
		
	#   date = '07-03-2022' # for debuging 
	rev_date = datetime.datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
	
	df = scrap_data(date)
	
	try:
		if df == None:
			print('Nothing found')
			return
	except:
		xd = 69
	
	#   Data,Otwarcie,Zamknięcie,Maks.,Min.,Obrót (mln. zł),Zmiana (%)
	#   Nazwa, Kod ISIN, Waluta, Kurs otwarcia, Kurs maksymalny, Kurs minimalny, Kurs zamknięcia, Zmiana kursu %, Wolumen obrotu (w szt.), Liczba transakcji, Wartość obrotu (w tys.)
	
	isin_list = {df['Kod ISIN'][i]: i for i in range(len(df))}
	df.drop(labels = ['Nazwa', 'Kod ISIN', 'Waluta', 'Wolumen obrotu (w szt.)', 'Liczba transakcji'], axis = 1, inplace = True)
	df.rename(columns = {'Kurs otwarcia' : 'Otwarcie', 'Kurs maksymalny' : 'Maks.', 'Kurs minimalny' : 'Min.', 'Kurs zamknięcia' : 'Zamknięcie', 'Zmiana kursu %' : 'Zmiana (%)', 'Wartość obrotu (w tys.)': 'Obrót (mln. zł)'}, inplace = True)
	df['Data'] = [rev_date] * len(df)
	#   df['Obrót (mln. zł)'] = [float(i) / 1000 for i in df['Obrót (mln. zł)']]
	#   ok, 'Obrót' column is 1000 times larger than it should be, but I don't want to fix it rn
	
	
	for f in os.listdir('./data_files/'):
		#   if f != 'xyz.csv':
		if f[0] > 'Z':
			continue
		print("doing " + str(f), end = '	')
		isin = ''
		try:
			with open('./info_files/' + f[:3] + '.info', 'r') as tmp:
				isin = form(tmp.readlines()[1])
		except:
			print('no info file!')
			continue
		
		print('isin = {}'.format(isin), end = ' ')
		real = pd.read_csv('./data_files/' + f)
		#   real.concat(df[0])
		try:
			real.loc[len(real)] = df.loc[isin_list[isin]] # [None for i in range(len(real.columns))]
			real.sort_values('Data', axis = 0, ascending = False, inplace = True)
			real.to_csv('./data_files/' + str(f), mode = 'w', index = False, header = True)
		except:
			print("stock wasn't active that day")
		#   print(real)
		print()
	
	return
	
	

if __name__ == "__main__":
	main()
