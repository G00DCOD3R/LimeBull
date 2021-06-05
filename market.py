import pandas as pd
import datetime, sys, math
import numpy as np
import matplotlib.pyplot as plt

class market: 
	#   class for handling market operations, as retrieving prices 
	def __init__(self):
		print("what stocks do you want to trade?\nWrite their 3 letter short name, all in one line\nExample: ABC XYZ DEF")
		self.stock_names = input().split()
		self.df = []
		self.name_to_number = {}
		self.day_counter = 0
		self.N = len(self.stock_names)
		cnt = 0
		for STOCK_NAME in self.stock_names:
			try:
				tmp = pd.read_csv("data_files/" + STOCK_NAME + ".csv", index_col = "Data", parse_dates = True)
				tmp = tmp[::-1]
				if cnt != 0:
					for i in tmp.index:
						if not (i in self.df[0].index):
							tmp.drop(i, inplace = True)
					for i in self.df[0].index:
						if not (i in tmp.index):
							for j in range(0, cnt):
								self.df[j].drop(i, inplace = True)
				
			except:
				print("No such asset " + str(STOCK_NAME))
				
			self.df.append(tmp)
			self.name_to_number[STOCK_NAME] = cnt
			cnt += 1
		print("market initialized successfully!")
			
	def show(self):
		#   shows today's prices
		print("prices today:")
		n = self.N
		for i in range(0, n):
			print(str(self.stock_names[i]) + " = " + str(self.asset_prices[i]))
		print("-------------\n")
		
	
	def price_today(self):
		#   returns a list of today's prices and copies it to self.asset_prices
		n = self.N
		if self.day_counter >= len(self.df[0]):
			return False
		self.asset_prices = [0] * n
		for i in range(0, n):
			self.asset_prices[i] = self.df[i]['Zamknięcie'][self.day_counter]
		self.day_counter += 1
		return self.asset_prices
		
class wallet:
	#   class for handling your wallet and buying/selling stocks
	def __init__(self, budget, N, stock_names):
		self.budget = budget 
		self.N = N
		self.stocks = [0] * N
		self.stock_names = stock_names	
	
	def eval_price(self, asset_prices):
		total = self.budget
		for i in range(0, self.N):
			total += self.stocks[i] * asset_prices[i]
		return total
	
	def show(self, asset_prices):
		#   gives a short description of your wallet
		#   such as:
		#   stock name, it's volume, today's price, weight percentage, total price
		
		print("\nThis is your wallet:")
		print("Name   volume   cur.price   weight%   total\n")
		n = self.N
		total = self.eval_price(asset_prices)
		print("cash: {}zl   {:.2f}%".format(self.budget, self.budget / total * 100))
		for i in range(0, n):
			tmp = self.stocks[i] * asset_prices[i]
			print("{}:   {}   {}zl   {:.2f}%   {}zl".format(self.stock_names[i], self.stocks[i], asset_prices[i], tmp / total * 100, tmp))
		print("TOTAL = {}".format(total))
		print("====================\n")
	def buy(self, which, amount, asset_prices):
		price = asset_prices[which] * amount
		if price > self.budget:
			print("Not enough money to buy {}".format(self.stock_names[which]))
			return False
		print(f'\033[{92}m', "Bought {} {} stocks for {}zl".format(amount, self.stock_names[which], asset_prices[which]), f'\033[{0}m')
		self.budget -= price
		self.stocks[which] += amount
		return True
	def sell(self, which, amount, asset_prices):
		price = asset_prices[which] * amount
		if stocks[which] < amount:
			print("Not enough stocks to sell {}".format(self.stock_names[which]))
			return False
		print(f'\033[{91}m', "Sold {} {} stocks for {}zl".format(amount, self.stock_names[which], asset_prices[which]), f'\033[{0}m')
		self.budget += price
		self.stocks[which] -= amount
		return True

def BuyAndHold(starting_budget):
	#   Benchmark strat, buy equally all stocks and hold them until the end of simulation
	
	print("\nDoing 'BuyAndHold' now")
	M = market()
	df = {}
	df['Data'] = M.df[0].index
	Wallet = [0] * len(df['Data'])
	me = wallet(starting_budget, M.N, M.stock_names)
	prices = M.price_today()
	Wallet[0] = me.eval_price(prices)
	for i in range(0, M.N):
		amount = math.floor(starting_budget / M.N / prices[i])
		me.buy(i, amount, prices)
	#   me.show(prices)
	
	for tur in range(1, 10 ** 8):
		prices = M.price_today()
		try:
			Wallet[tur] = me.eval_price(prices)
		except:
			break
		if tur % 200 == 0:
			me.show(prices)
	df['Wallet'] = Wallet
	res = pd.DataFrame(df)
	res.set_index('Data')
	return res
	
def main(): 
	
	#   main function to keep all strats organized and plot graphs
	#   you initialize starting_budget, every strat should return
	#   a dataframe of form: ['Data', 'Wallet']
	#   you have to initialize market for every strat (I think it's simpler)
	
	starting_budget = 1000
	
	#   ALWAYS RENAME WHEN ADDING NEW STRAT!
	df = BuyAndHold(starting_budget)
	
	print(df)
	
	df.rename(columns = {'Wallet' : 'BENCHMARK'}, inplace = True)
	
	#   plotting all results, from different strats
	plt.figure(1, figsize=(20, 10))
	plt.plot(df['BENCHMARK'], 'r-', label = 'BENCHMARK')
	plt.legend()
	plt.title('Strats Comparing')
	
	plt.show()
	


if __name__ == "__main__":
	main()
	
