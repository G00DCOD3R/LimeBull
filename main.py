import pandas as pd
import datetime, sys, math
import numpy as np
import matplotlib.pyplot as plt

class market:
	def __init__(self):
		if len(sys.argv) == 1:
			raise Error("Specify stock name you want to track")
		STOCK_NAME = sys.argv[1]
		self.df = pd.read_csv("data_files/" + STOCK_NAME + ".csv", index_col = "Data", parse_dates = True)
		self.wig_df = pd.read_csv("data_files/WIG.csv", index_col = 'Data', parse_dates = True)
		self.df = self.df[::-1]
		
		#   print("Enter start date (format Y-m-d):")
		#   self.Start_date = input()
		#   print("Enter end date (format Y-m-d):")
		#   self.End_date = input()
		#   self.Start_date = datetime.datetime.strptime(self.Start_date, "%Y-%m-%d")
		#   self.End_date = datetime.datetime.strptime(self.End_date, "%Y-%m-%d")	
		
		self.Start_date = datetime.date(2008, 1, 1)
		self.End_date = datetime.date(2021, 3, 1)
		# debug purposes y-m-d
		
		self.df = self.df[self.Start_date:self.End_date]
		self.wig_df = self.wig_df[self.Start_date:self.End_date]
		
		for i in self.df.index:
			if not (i in self.wig_df.index):
				self.df.drop(i, inplace = True)
		for i in self.wig_df.index:
			if not (i in self.df.index):
				self.wig_df.drop(i, inplace = True)
		
		#   print(len(self.df), len(self.wig_df))
		
		self.df['UpperBol'] = np.empty(len(self.df), dtype=object)
		self.df['LowerBol'] = np.empty(len(self.df), dtype=object)
		self.df['SMA'] = np.empty(len(self.df), dtype=object)
		self.df['RSI'] = np.empty(len(self.df), dtype=object)
		self.wig_df['RSI'] = np.empty(len(self.df), dtype=object)
		self.wig_df['change'] = np.empty(len(self.df), dtype=object)
		self.df['change'] = np.empty(len(self.df), dtype=object)
		self.df['wallet_size'] = np.empty(len(self.df), dtype=object)
		#   self.df['change'] = (self.df['Otwarcie'] - self.df['Zamknięcie']) / self.df['Otwarcie']
		#   self.wig_df['change'] = (self.wig_df['Otwarcie'] - self.wig_df['Zamknięcie']) / self.wig_df['Otwarcie']
		
		self.which_day = 0
		
	def get_price(self):
		if self.which_day == len(self.df):
			return False
		ans = self.df['Zamknięcie'][self.which_day]
		wig_ans = self.wig_df['Zamknięcie'][self.which_day]
		Open = self.df['Otwarcie'][self.which_day]
		wig_Open = self.wig_df['Otwarcie'][self.which_day]
		self.which_day += 1
		return (ans, wig_ans, Open, wig_Open)

class wallet:
	def __init__(self, capital):
		self.capital = capital
		self.stocks = {'A':0}
	def buy(self, amount, price):
		if amount * price[0]  > self.capital:
			print("Not enough money to buy {} stocks for {}zlf'\033[{0}m'".format(amount, price))
			return
		self.capital -= amount * price
		self.stocks['A'] += amount
		print(f'\033[{92}m', "Bought {} stocks for {}zl".format(amount, price), f'\033[{0}m')
	def sell(self, amount, price):
		if amount > self.stocks['A']:
			print("Not enough stocks to sell {} of them for {}zl".format(amount, price))
			return
		self.capital += amount * price[0]
		self.stocks['A'] -= amount
		print(f'\033[{91}m', "Sold {} stocks for {}zl".format(amount, price), f'\033[{0}m')
	def wallet_size(self, price):
		return self.capital + self.stocks['A'] * price[0]

def rsi_calc(arr):
	total_win, total_lose = 0, 0
	for i in arr:
		if i > 0:
			total_win += i
		else:
			total_lose -= i
	if total_lose == 0:
		return 100
	ans = 100 - (100 / (1 + total_win / total_lose))
	return ans

def main():
	
	M = market()
	me = wallet(100000)
	
	WINDOW_SIZE = 21
	RSI_WINDOW_SIZE = 10
	
	
	
	benchmark_start_size = me.capital // M.df['Zamknięcie'][0]
	M.df['BENCHMARK'] = M.df['Zamknięcie'] * benchmark_start_size + (me.capital - benchmark_start_size * M.df['Zamknięcie'][0])
	N = len(M.df) # length of simulation
	
	prices = np.zeros((N,1))
	wig_prices = np.zeros((N,1))
	for day in range(WINDOW_SIZE - 1):
		Open, wig_Open = 0, 0
		(prices[day], wig_prices[day], Open, wig_Open) = M.get_price()
		if prices[day] == False:
			print("Not enough data!")
			return
		M.df.loc[M.df.index[day], 'change'] = (Open - prices[day]) / Open
		M.wig_df.loc[M.wig_df.index[day], 'change'] = (wig_Open - wig_prices[day]) / wig_Open
		M.df[M.df.index[day], 'wallet_size'] = me.capital
	
	for day in range(WINDOW_SIZE - 1, N):
		(prices[day], wig_prices[day], Open, wig_Open) = M.get_price()
		if prices[day] == False:
			print("End of simulation")
			break
		
		M.df.loc[M.df.index[day], 'change'] = (Open - prices[day]) / Open
		M.wig_df.loc[M.wig_df.index[day], 'change'] = (wig_Open - wig_prices[day]) / wig_Open
		
		deviation = np.std(prices[day-WINDOW_SIZE + 1:day+1])
		M.df.loc[M.df.index[day], 'SMA'] = prices[day-WINDOW_SIZE + 1:day+1].mean()
		M.df.loc[M.df.index[day],'UpperBol'] = prices[day-WINDOW_SIZE + 1:day+1].mean() + 2 * deviation
		M.df.loc[M.df.index[day],'LowerBol'] = prices[day-WINDOW_SIZE +1:day+1].mean() - 2 * deviation
		
		M.df.loc[M.df.index[day],'RSI'] = rsi_calc(M.df['change'][day-RSI_WINDOW_SIZE+1:day+1])
		M.wig_df.loc[M.df.index[day],'RSI'] = rsi_calc(M.wig_df['change'][day-RSI_WINDOW_SIZE+1:day+1])
		
		BB_value = (prices[day] - M.df['SMA'][day]) / (2 * deviation)
		stock_RSI = M.df['RSI'][day]
		wig_RSI = M.wig_df['RSI'][day]
		
		#   Lower than -1 -> Buy; Higher than 1 -> Sell
		#   RSI less than 30 -> buy; Higher than 70 -> Sell
		#   different signs with wig_RSI
		
		#   print("BB={}, sRSI={}, wRSI={}".format(BB_value, stock_RSI, wig_RSI))
		
		
		if BB_value <= -0.9:
			can = math.floor((me.capital * 0.15) // prices[day])
			if can > 0:
				me.buy(can, prices[day])
		elif BB_value >= 0.9:
			can = math.floor(me.stocks['A'] * prices[day] * 0.15) // prices[day]
			if can > 0:
				me.sell(can, prices[day])
		
		M.df.loc[M.df.index[day], 'wallet_size'] = me.wallet_size(prices[day])
	
	print(me.capital)
	print(me.stocks)	
	print(me.wallet_size(prices[N - 1]))
	
		
	plt.figure(1, figsize=(20,10))
	
	plt.plot(M.df['SMA'], 'y:', label="SMA")
	plt.plot(M.df['UpperBol'], 'g--', label="Upper")
	plt.plot(M.df['LowerBol'], 'r--', label="Lower")
	plt.plot(M.df['Zamknięcie'], 'b-', label="Zamknięcie")
	plt.legend()
	plt.title('Bollinger bands')
	
	plt.figure(2, figsize=(20, 10))
		
	plt.plot(M.df['RSI'], 'b-', label = 'stock RSI')
	plt.plot(M.wig_df['RSI'], 'k-', label = 'wig RSI')
	
	#   plt.plot(M.df['horizontal_30'], 'r--', label = 'Lower')
	#   plt.plot(M.df['horizontal_70'], 'g--', label = 'Upper')
	
	plt.legend()
	plt.title('RSI')
	
	plt.figure(3, figsize=(20, 10))
	
	plt.plot(M.df['BENCHMARK'], 'r-', label = 'benchmark')
	plt.plot(M.df['wallet_size'], 'g-', label = 'wallet')
	plt.legend()
	plt.title('Comparing')
	
	plt.show()
	
	
if __name__ == "__main__":
	main()

