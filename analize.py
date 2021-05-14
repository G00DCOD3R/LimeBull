import pandas as pd
import matplotlib.pyplot as plt
import datetime, sys

#   Program that analise historical stock prices

def sd3(arr):
	#   standard deviation with 3rd powers
	#   use on rolling windows
	#   as in example: 
	#   df["test2"] = df['Zamknięcie'].rolling(window = 20).mean() - 2 * df['Zamknięcie'].rolling(window = 20).apply(lambda x: sd3(x))
	
	sm = 0
	mean = arr.mean()
	for i in arr:
		sm += abs(i - mean) ** 3
	n = len(arr)
	sm /= n
	sm = sm ** (1 / 3)
	return sm
	
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
	if len(sys.argv) == 1:
		raise Error("Specify stock name you want to track")
	STOCK_NAME = sys.argv[1]
	df = pd.read_csv("data_files/" + STOCK_NAME + ".csv", index_col = "Data", parse_dates = True)
	wig_df = pd.read_csv("data_files/WIG.csv", index_col = "Data", parse_dates = True)
	if STOCK_NAME != 'WIG':
		df = df[::-1]
		#   WIG is already reversed ;)
	#   reading dataframe
	
	if True == False:	
		#   do you want to specify exact date of tracking?
		#   500 most recent days, otherwise
		print("Enter start date (format Y-m-d):")
		Start_date = input()
		print("Enter end date (format Y-m-d):")
		End_date = input()
		Start_date = datetime.datetime.strptime(Start_date, "%Y-%m-%d")
		End_date = datetime.datetime.strptime(End_date, "%Y-%m-%d")	
		df = df[Start_date:End_date]
		wig_df = wig_df[Start_date:End_date]
	else:
		DAYS_BACK = 500
		df = df[-DAYS_BACK:]
		wig_df = wig_df[-DAYS_BACK:]
	
	#   df["EWMA"] = df["Zamknięcie"].ewm(halflife = 0.5, min_periods = 200).mean()
	#   ewm mean, idk what it does
	
	df['change'] = (df['Otwarcie'] - df['Zamknięcie']) / df['Otwarcie']
	wig_df['change'] = (wig_df['Otwarcie'] - wig_df['Zamknięcie']) / wig_df['Otwarcie']
	
	WINDOW_SIZE = 25
	
	df["SMA"] = df['Zamknięcie'].rolling(window = WINDOW_SIZE).mean()
	df["Upper"] = df['Zamknięcie'].rolling(window = WINDOW_SIZE).mean() + df['Zamknięcie'].rolling(window = WINDOW_SIZE).std() * 2
	df["Lower"] = df['Zamknięcie'].rolling(window = WINDOW_SIZE).mean() - df['Zamknięcie'].rolling(window = WINDOW_SIZE).std() * 2
	#   Bollinger bands and moving average 
	#   You can change multipliers
	
	df['RSI'] = df['change'].rolling(window = WINDOW_SIZE).apply(lambda x: rsi_calc(x))
	wig_df['RSI'] = wig_df['change'].rolling(window = WINDOW_SIZE).apply(lambda x: rsi_calc(x))
	#   RSI calculation
	
	df['horizontal_30'] = [30] * len(df)
	df['horizontal_70'] = [70] * len(df)
	
	#   START OF PLOTTING
	
	plt.figure(1, figsize=(20,10))
	
	plt.plot(df['SMA'], 'y:', label="SMA")
	plt.plot(df['Upper'], 'g--', label="Upper")
	plt.plot(df['Lower'], 'r--', label="Lower")
	plt.plot(df['Zamknięcie'], 'b-', label="Zamknięcie")
	plt.legend()
	plt.title('Bollinger bands')
	
	if STOCK_NAME != 'WIG':
		plt.figure(2, figsize=(20, 10))
		
		plt.plot(df['RSI'], 'b-', label = 'stock RSI')
		plt.plot(wig_df['RSI'], 'k-', label = 'wig RSI')
		plt.plot(df['horizontal_30'], 'r--', label = 'Lower')
		plt.plot(df['horizontal_70'], 'g--', label = 'Upper')
		plt.legend()
		plt.title('RSI')
		
		
		
	plt.show()

if __name__ == "__main__":
	main()
