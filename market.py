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
		if len(self.df[0].index) < 200:
			print("WARNING! short backtesting period".format(len(self.df[0].index)), end = " ")
		print("Backtesting {} days".format(len(self.df[0].index)))
		print("market initialized successfully!\n")
			
	def show(self):
		#   shows today's prices
		print("prices today:")
		n = self.N
		for i in range(0, n):
			print(str(self.stock_names[i]) + " = " + str(self.asset_prices[i]))
		print("-------------\n")
		
	def reset(self):
		self.day_counter = 0
	
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

GLOB_MARKET = market()

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
		return round(total, 2)
	
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
			tmp = round(self.stocks[i] * asset_prices[i], 2)
			print("{}:   {}   {}zl   {:.2f}%   {}zl".format(self.stock_names[i], self.stocks[i], asset_prices[i], tmp / total * 100, tmp))
		print("TOTAL = {}".format(total))
		print("====================\n")
	def buy(self, which, amount, asset_prices):
		if amount == 0:
			return False
		price = asset_prices[which] * amount
		if price > self.budget:
			print("Not enough money to buy {}".format(self.stock_names[which]))
			return False
		#   print(f'\033[{92}m', "Bought {} {} stocks for {}zl".format(amount, self.stock_names[which], asset_prices[which]), f'\033[{0}m')
		self.budget -= price
		self.stocks[which] += amount
		self.budget = round(self.budget, 2)
		return True
	def sell(self, which, amount, asset_prices):
		if amount == 0:
			return False
		price = asset_prices[which] * amount
		if self.stocks[which] < amount:
			print("Not enough stocks to sell {}".format(self.stock_names[which]))
			return False
		#   print(f'\033[{91}m', "Sold {} {} stocks for {}zl".format(amount, self.stock_names[which], asset_prices[which]), f'\033[{0}m')
		self.budget += price
		self.stocks[which] -= amount
		self.budget = round(self.budget, 2)
		return True

def BuyAndHold(starting_budget):
	#   Benchmark strat, buy equally all stocks and hold them until the end of simulation
	
	print("\nDoing 'BuyAndHold' now")
	M = GLOB_MARKET
	df = {}
	df['Data'] = M.df[0].index
	Wallet = [0] * len(df['Data'])
	me = wallet(starting_budget, M.N, M.stock_names)
	prices = M.price_today()
	Wallet[0] = me.eval_price(prices)
	#   part that every strat should contain
	
	for i in range(0, M.N):
		amount = math.floor(starting_budget / M.N / prices[i])
		me.buy(i, amount, prices)
	#   me.show(prices)
	
	for tur in range(1, 10 ** 8):
		tmp_prices = prices
		prices = M.price_today()
		try:
			Wallet[tur] = me.eval_price(prices)
		except:
			me.show(tmp_prices)
			break
		#   if tur % 360 == 0:
			#   me.show(prices)
	df['Wallet'] = Wallet
	
	res = pd.DataFrame(df)
	res.set_index('Data', inplace = True)
	GLOB_MARKET.reset()
	return res
	
def MomentumRotational(starting_budget, rebalance_period, top):
	# Every n days it takes stock with the best momentum factor and holds it for the next period
	
	print("\nDoing MomentumRotational now")
	M = GLOB_MARKET
	df = {}
	df['Data'] = M.df[0].index
	Wallet = [0] * len(df['Data'])
	me = wallet(starting_budget, M.N, M.stock_names)
	prices = M.price_today()
	Wallet[0] = me.eval_price(prices)
	top = min(top, M.N)
	#   part that every strat should contain
	
	prev_prices = prices
	for tur in range(1, 10 ** 8):
		prices = M.price_today()
		if prices == False:
			break
		if tur % rebalance_period == 0:
			#   rebalance (could be different function)
			momentum = []
			for i in range(M.N):
				val = (prices[i] - prev_prices[i]) / prev_prices[i]
				momentum.append((val, i))
			momentum.sort(reverse = True)
			to_buy = momentum[0:top]
			for i in range(me.N): # selling all stocks
				if me.stocks[i] > 0:
					me.sell(i, me.stocks[i], prices)
			cap = round(me.budget * .5 / len(to_buy), 2) # how much money for one asset
			for i in to_buy:
				if i[0] < 0:
					continue
				who = i[1]
				amount = math.floor(cap / prices[who])
				me.buy(who, amount, prices)
			prev_prices = prices
		Wallet[tur] = me.eval_price(prices)
		if tur % 360 == 0:
			me.show(prices)
		
	df['Wallet'] = Wallet
	
	res = pd.DataFrame(df)
	res.set_index('Data', inplace = True)
	GLOB_MARKET.reset()
	return res

def MACDNormal(starting_budget, kelly):
	# Every n days it takes stock with the best momentum factor and holds it for the next period
	# MACD crosses above signal -> buy (MACD was above, now below). Otherwise sell (crosses below)
	# So far the best strat ;) 
	
	print("\nDoing MACDNormal now")
	M = GLOB_MARKET
	df = {}
	df['Data'] = M.df[0].index
	Wallet = [0] * len(df['Data'])
	me = wallet(starting_budget, M.N, M.stock_names)
	prices = M.price_today()
	Wallet[0] = me.eval_price(prices)
	#   part that every strat should contain
	
	def next_ema(prev, cur, periods):
		# calculating next ema, based
		# on previous and current prices
		# smoothing can be changed
		# prev and cur are lists of the same size
		res = [0] * len(cur)
		for i in range(len(cur)):
			smoothing = 2
			factor = smoothing / (periods + 1)
			res[i] = factor * cur[i] + (1 - factor) * prev[i]
		return res
	
	short_term = 12
	long_term = 26
	signal_term = 9
	short_ema = prices
	long_ema = prices
	macd_signal = [0] * len(prices)
	below = [False] * len(prices) # MACD below signal
	last_operation = [0] * len(prices) # price of the last transaction, to calculate profit
	ops_done = 0 # sells done
	win_profit = 0 # sum of profits
	lose_profit = 0 # sum of loses
	wins_count = 0
	#   kelly = 0.60 # bet percentage
	
	for tur in range(1, 10 ** 8):
		tmp_prices = prices
		prices = M.price_today()
		if prices == False:
			me.show(tmp_prices)
			break
			
		#   calculating emas 
		short_ema = next_ema(short_ema, prices, short_term)
		long_ema = next_ema(long_ema, prices, long_term)
		diff = [short_ema[i] - long_ema[i] for i in range(0, len(prices))]
		macd_signal = next_ema(macd_signal, diff, signal_term)
		
		want_buy = []
		for i in range(len(prices)):
			if diff[i] < macd_signal[i] and below[i] == False: # buy stock
				want_buy.append(i)
				last_operation[i] = prices[i]
				
			if diff[i] > macd_signal[i] and below[i] == True: # sell stock
				amount = round(me.stocks[i] * kelly)
				me.sell(i, amount, prices)
				win_profit += max(.0, (prices[i] - last_operation[i])/last_operation[i])
				lose_profit += min(.0, (prices[i] - last_operation[i])/last_operation[i])
				
				if(prices[i] > last_operation[i]):
					wins_count += 1
				ops_done += 1
				
			if diff[i] < macd_signal[i]:
				below[i] = True
			else:
				below[i] = False
		if len(want_buy) > 0:
			cap = round(me.budget * kelly / len(want_buy), 2)
			for i in want_buy:
				amount = math.floor(cap / prices[i])
				me.buy(i, amount, prices)
		
		
		Wallet[tur] = me.eval_price(prices)
		#   if tur % 365 == 0:
			#   me.show(prices)
		
	df['Wallet'] = Wallet
	
	win_profit /= wins_count
	lose_profit /= (ops_done - wins_count)
	lose_profit *= -1
	
	print("Average winnning gain is {}\nAverage lose is {}\nAverage win ratio is {:.2f}".format(win_profit, lose_profit, wins_count / ops_done))
	
	res = pd.DataFrame(df)
	res.set_index('Data', inplace = True)
	GLOB_MARKET.reset()
	return res
def MACDWithKelly(starting_budget):
	# Every n days it takes stock with the best momentum factor and holds it for the next period
	# MACD crosses above signal -> buy (MACD was above, now below). Otherwise sell (crosses below)
	# So far the best strat ;) 
	
	print("\nDoing MACDWithKelly now")
	M = GLOB_MARKET
	df = {}
	df['Data'] = M.df[0].index
	Wallet = [0] * len(df['Data'])
	me = wallet(starting_budget, M.N, M.stock_names)
	prices = M.price_today()
	Wallet[0] = me.eval_price(prices)
	#   part that every strat should contain
	
	kelly = .1
	
	def next_ema(prev, cur, periods):
		# calculating next ema, based
		# on previous and current prices
		# smoothing can be changed
		# prev and cur are lists of the same size
		res = [0] * len(cur)
		for i in range(len(cur)):
			smoothing = 2
			factor = smoothing / (periods + 1)
			res[i] = factor * cur[i] + (1 - factor) * prev[i]
		return res
	
	short_term = 12
	long_term = 26
	signal_term = 9
	short_ema = prices
	long_ema = prices
	macd_signal = [0] * len(prices)
	below = [False] * len(prices) # MACD below signal
	last_operation = [0] * len(prices) # price of the last transaction, to calculate profit
	ops_done = 0 # sells done
	win_profit = 0 # sum of profits
	lose_profit = 0 # sum of loses
	wins_count = 0
	#   kelly = 0.60 # bet percentage
	
	profits = []
	
	for tur in range(1, 10 ** 8):
		tmp_prices = prices
		prices = M.price_today()
		if prices == False:
			me.show(tmp_prices)
			break
			
		#   calculating emas 
		short_ema = next_ema(short_ema, prices, short_term)
		long_ema = next_ema(long_ema, prices, long_term)
		diff = [short_ema[i] - long_ema[i] for i in range(0, len(prices))]
		macd_signal = next_ema(macd_signal, diff, signal_term)
		
		want_buy = []
		for i in range(len(prices)):
			if diff[i] < macd_signal[i] and below[i] == False: # buy stock
				want_buy.append(i)
				last_operation[i] = prices[i]
				
			if diff[i] > macd_signal[i] and below[i] == True: # sell stock
				amount = round(me.stocks[i] * kelly)
				me.sell(i, amount, prices)
				profits.append((prices[i] - last_operation[i]) / last_operation[i])
				#   win_profit += max(.0, (prices[i] - last_operation[i])/last_operation[i])
				#   lose_profit += min(.0, (prices[i] - last_operation[i])/last_operation[i])
				
				wins_count = 0
				win_profit = lose_profit = 0
				#   print(len(profits))
				for j in range(0, min(30, len(profits))):
					if(profits[-j - 1] > 0):
						wins_count += 1
						win_profit += profits[-j-1]
					else:
						lose_profit -= profits[-j-1]
				if len(profits) >= 20:
					W = wins_count / (min(30, len(profits))) # win percentage
					try:
						kelly = W - (1 - W) / (win_profit / lose_profit)
					except:
						if win_profit == 0:
							kelly = .1
						else:
							kelly = .35
					kelly = min(kelly, .5)
					kelly = max(kelly, 0.1)
				
			if diff[i] < macd_signal[i]:
				below[i] = True
			else:
				below[i] = False
		if len(want_buy) > 0:
			cap = round(me.budget * kelly / len(want_buy), 2)
			for i in want_buy:
				amount = math.floor(cap / prices[i])
				me.buy(i, amount, prices)
		
		
		Wallet[tur] = me.eval_price(prices)
		#   if tur % 365 == 0:
			#   me.show(prices)
		
	df['Wallet'] = Wallet
	
	ops_done = len(profits)
	win_profit = lose_profit = wins_count = 0
	for i in profits:
		if i > 0:
			wins_count += 1
			win_profit += i
		else:
			lose_profit -= i
	
	win_profit /= wins_count
	lose_profit /= (ops_done - wins_count)
	lose_profit *= -1
	
	print("Average winnning gain is {}\nAverage lose is {}\nAverage win ratio is {:.2f}".format(win_profit, lose_profit, wins_count / ops_done))
	
	res = pd.DataFrame(df)
	res.set_index('Data', inplace = True)
	GLOB_MARKET.reset()
	return res
	
def main(): 
	
	#   main function to keep all strats organized and plot graphs
	#   you initialize starting_budget, every strat should return
	#   a dataframe of form: ['Data', 'Wallet']
	#   you have to initialize market for every strat (I think it's simpler), but slower!!!
	#   considering doing separate classes for every strat, to make it even more convienent
	
	starting_budget = 100
	
	#   ALWAYS RENAME WHEN ADDING NEW STRAT!
	
	df = BuyAndHold(starting_budget)
	df['st.cap.'] = [starting_budget] * len(df.index)
	
	df.rename(columns = {'Wallet' : 'BENCHMARK'}, inplace = True)
	
	#   tmp = MomentumRotational(starting_budget, 21, 3)
	#   df['TOP3'] = tmp['Wallet']
	
	tmp = MACDWithKelly(starting_budget)
	df['Kelly'] = tmp['Wallet']
	tmp = MACDNormal(starting_budget, 0.7)
	df['High'] = tmp['Wallet']
	
	#   plotting all results, from different strats
	plt.figure(1, figsize=(20, 10))
	plt.plot(df['BENCHMARK'], 'r-', label = 'BENCHMARK')
	#   plt.plot(df['TOP3'], 'b-', label = 'TOP3')
	plt.plot(df['Kelly'], 'g-', label = 'Kelly')
	plt.plot(df['High'], 'b-', label = 'High')
	plt.plot(df['st.cap.'], 'k:', label = 'Starting Capital')
	plt.legend()
	plt.title('Strats Comparing')
	
	plt.show()
	


if __name__ == "__main__":
	main()
	
