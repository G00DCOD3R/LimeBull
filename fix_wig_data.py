import os
import pandas as pd
import datetime


def main():
	#   so investing.com is providing some 'stupid' coding of WIG which is a polish market index 
	#   this scrip tries to fix the issue
	#   at least it works :)))
	
	
	
	file_to_fix = './data_files/WIG.csv'
	lines = []
	result = []
	first_skip = True
	
	with open(file_to_fix, 'r') as infile:
		lines = infile.readlines()
	for line in lines:
		tmp = line.split('","')
		tmp[0] = tmp[0][1:]
		tmp[-1] = tmp[-1][:-2]
		if first_skip:
			result.append(','.join(tmp))
			first_skip = False
			continue
		tmp[0] = datetime.datetime.strptime(tmp[0], '%b %d, %Y').strftime('%Y-%m-%d')
		for i in range(1, len(tmp)):
			tmp[i] = "".join(tmp[i].split(","))
		result.append(",".join(tmp))
	with open(file_to_fix, 'w') as outfile:
		for i in result:
			outfile.write(i)
			outfile.write('\n')
	
	print('please fix the last row in your dataframe')

if __name__ == "__main__":
	main()
