import os, sys
import pandas as pd

def equalize_dataframes(df_A, df_B):
	#   returns dataframe with same dates (removes appearances of dates that occur only in one df)
	
	pos_A = pos_B = 0
	df = {'Data':[], 'A':[], 'B':[]}
	len_A = len(df_A)
	len_B = len(df_B)
	while pos_A < len_A and pos_B < len_B:
		while pos_A < len_A and pos_B < len_B and df_A['Data'][pos_A] != df_B['Data'][pos_B]:
			while pos_A < len_A and pos_B < len_B and df_A['Data'][pos_A] > df_B['Data'][pos_B]:
				pos_A += 1
			while pos_A < len_A and pos_B < len_B and df_B['Data'][pos_B] > df_A['Data'][pos_A]:
				pos_B += 1
		if pos_A < len_A and pos_B < len_B:
			df['Data'].append(df_A['Data'][pos_A])
			#   df['DataB'].append(df_B['Data'][pos_B])
			df['A'].append(df_A['Zamknięcie'][pos_A])
			df['B'].append(df_B['Zamknięcie'][pos_B])
			pos_A += 1
			pos_B += 1
	for i in df:
		df[i] = df[i][::-1]
	df = pd.DataFrame(df)
	return df


def get_correlation(df, N, lookback):
	#   it returns a list of correlation values for each value in df (column 'A' vs col 'B')
	#   with a window_size = N (sample size) and lookback means we consider only last 'lookback' prices
	
	df2 = pd.DataFrame()
	df2['change_A'] = df['A']
	df2['change_B'] = df['B']
	for i in range(1, len(df)):
		df2['change_A'][i] = df['A'][i] / df['A'][i-1] - 1
		df2['change_B'][i] = df['B'][i] / df['B'][i-1] - 1
	df2['change_A'][0] = df2['change_B'][0] = 0
	
	df2['mean_A'] = df2['change_A'].rolling(window = N).mean()
	df2['mean_B'] = df2['change_B'].rolling(window = N).mean()
	
	#   standard deviations below:
	df2['sd_A'] = df2['change_A'].rolling(window = N).std() 
	df2['sd_B'] = df2['change_B'].rolling(window = N).std()
	
	res = [None] * len(df2)
	
	for i in range(max(N-1, len(df2) - lookback), len(df2)): # it will calculate correlation based on 400 last prices
		covariance = 0
		if df2['sd_B'][i] == 0 or df2['sd_A'][i] == 0:
			print('Zero problem encountered, try larger N')
			#   print('Problem is here:') # stuff for debugging wrong data
			#   print(i)
			#   for j in range(i-N+1, i+1):
				#   print('{} {} {}'.format(df2['change_A'][j], df2['mean_A'][i], df['Data'][j]))
			return None
		for j in range(i-N+1, i+1):
			covariance += (df2['change_A'][j] - df2['mean_A'][i]) * (df2['change_B'][j] - df2['mean_B'][i])
		
		covariance /= (N-1) * df2['sd_A'][i] * df2['sd_B'][i]
		res[i] = round(covariance, 4)
	return res
	



def main():
	
	#   what you can adjust here:
		#   in get_correlation() N and lookback
		#   in correlation_bounds the upper and lower limit for determining correlations
	#   now it takes 5 minutes for 30 stocks and 1yr lookback
	
	files = os.listdir('./data_files')
	
	#   print("two stocks separated by one space example: ABC XYZ")
	#   [stock_A, stock_B] = input().split(' ')
	
	#   [stock_A, stock_B] = ['xyz', 'abc'] # debug stuff 
	
	correlations = []
	
	for i in range(len(files)):
		for j in range(i+1, len(files)):
			[stock_A, stock_B] = [files[i][:-4], files[j][:-4]]
			
			df_A = pd.read_csv('./data_files/' + stock_A + '.csv')
			df_B = pd.read_csv('./data_files/' + stock_B + '.csv')
			df_A['Zamknięcie'] = [float(i) for i in df_A['Zamknięcie']]
			df_B['Zamknięcie'] = [float(i) for i in df_B['Zamknięcie']]
			df = equalize_dataframes(df_A, df_B)
			
			#   for i in range(len(df)):
				#   print("{}: {} {}".format(df['Data'][i], df['A'][i], df['B'][i]))
			#   debug stuff 
			
			result_list = get_correlation(df, 20, 365)
			def mean(x):
				sm = cnt = 0
				for i in x:
					if i != None:
						sm += i
						cnt += 1
				return round(sm / cnt, 4)
			result = mean(result_list)
			print('{} + {} ----> {}'.format(stock_A, stock_B, result))
			correlations.append((result, stock_A, stock_B))
	correlations = sorted(correlations)
	
	correlation_bounds = [-0.4, 0.4]
	
	print()
	print()
	print('NEGATIVE CORRELATION: ')
	for i in correlations:
		if i[0] <= correlation_bounds[0]:
			print('({}, {}) --> {}'.format(i[1], i[2], i[0]))
		else:
			break
	print()
	print()
	print('NO CORRELATION: ')
	for i in correlations:
		if i[0] > correlation_bounds[0] and i[0] <= correlation_bounds[1]:
			print('({}, {}) --> {}'.format(i[1], i[2], i[0]))
		elif i[0] > correlation_bounds[1]:
			break
	
	print()
	print()
	print('POSITIVE CORRELATION: ')
	for i in correlations:
		if i[0] > correlation_bounds[1]:
			print('({}, {}) --> {}'.format(i[1], i[2], i[0]))
	


if __name__ == "__main__": 
	main()

