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
	#   part that every strat should contain
	
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
		if tur % 360 == 0:
			me.show(prices)
	df['Wallet'] = Wallet
	
	res = pd.DataFrame(df)
	res.set_index('Data', inplace = True)
	return res
	
def MomentumRotational(starting_budget, rebalance_period, top):
	# Every n days it takes stock with the best momentum factor and holds it for the next period
	
	print("\nDoing MomentumRotational now")
	M = market()
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
	return res
def MACDRotational(starting_budget, rebalance_period, top):
	# Every n days it takes stock with the best momentum factor and holds it for the next period
	
	print("\nDoing MACDRotational now")
	M = market()
	df = {}
	df['Data'] = M.df[0].index
	Wallet = [0] * len(df['Data'])
	me = wallet(starting_budget, M.N, M.stock_names)
	prices = M.price_today()
	Wallet[0] = me.eval_price(prices)
	top = min(top, M.N)
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
	for tur in range(1, 10 ** 8):
		prices = M.price_today()
		if prices == False:
			break
			
		#   calculating emas 
		short_ema = next_ema(short_ema, prices, short_term)
		long_ema = next_ema(long_ema, prices, long_term)
		diff = [short_ema[i] - long_ema[i] for i in range(0, len(prices))]
		macd_signal = next_ema(macd_signal, diff, signal_term)
		
		
		if tur % rebalance_period == 0:
			#   rebalance (could be different function)
			momentum = []
			for i in range(M.N):
				val = (diff[i] - macd_signal[i])
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
		Wallet[tur] = me.eval_price(prices)
		if tur % 360 == 0:
			me.show(prices)
		
	df['Wallet'] = Wallet
	
	res = pd.DataFrame(df)
	res.set_index('Data', inplace = True)
	return res
def MACDNormal(starting_budget):
	# Every n days it takes stock with the best momentum factor and holds it for the next period
	#   MACD > signal -> buy, otherwise sell
	
	print("\nDoing MACDNormal now")
	M = market()
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
	for tur in range(1, 10 ** 8):
		prices = M.price_today()
		if prices == False:
			break
			
		#   calculating emas 
		short_ema = next_ema(short_ema, prices, short_term)
		long_ema = next_ema(long_ema, prices, long_term)
		diff = [short_ema[i] - long_ema[i] for i in range(0, len(prices))]
		macd_signal = next_ema(macd_signal, diff, signal_term)
		
		want_buy = []
		for i in range(len(prices)):
			if diff[i] < macd_signal[i] and below[i] == False:
				want_buy.append(i)
			if diff[i] > macd_signal[i] and below[i] == True:
				me.sell(i, me.stocks[i], prices)
			if diff[i] < macd_signal[i]:
				below[i] = True
			else:
				below[i] = False
		if len(want_buy) > 0:
			cap = round(me.budget * 0.5 / len(want_buy), 2)
			for i in want_buy:
				amount = math.floor(cap / prices[i])
				me.buy(i, amount, prices)
		
		
		Wallet[tur] = me.eval_price(prices)
		if tur % 360 == 0:
			me.show(prices)
		
	df['Wallet'] = Wallet
	
	res = pd.DataFrame(df)
	res.set_index('Data', inplace = True)
	return res
