import os, sys
import pandas as pd

def main():
	path = '/home/tymon/Programy/C++/gh/tradde'
	files = os.listdir(path + '/data_files')
	too_short = []
	#   pd.options.mode.chained_assignment = None # please revise it asap, because now it's too late UPDATE, should work fine now
	
	
	for f in files:
		#   if(f != 'xyz.csv'):
			#   continue
		
		print('checking ' + str(f) + ' now	', end = '')
		
		NAME = f[:-4]
		try:
			temp_name = ''
			with open(path + '/info_files/' + NAME + '.info', 'r') as tmp:
				temp_name = tmp.readlines()[0][:65]
				
			#   optional, I used it to get ISIN numbers from urls, without it we just don't change .info 
			#   with open('./info_files/' + NAME + '.info', 'w') as tmp:
				#   tmp.write(str(temp_name))
				#   tmp.write(str('\n' + temp_name[39:51] + '\n'))
		except:
			print('no info file!', end = '	')
		
		
		
		
		#   removing not unique elements + sorting
		df = pd.read_csv('./data_files/' + str(f))
		used = set()
		sorting_correction = False
		for i in df.index:
			if df['Data'][i] in used:
				df.drop(labels = i, axis = 0, inplace = True)
				sorting_correction = True
			else:
				used.add(df['Data'][i])

		if sorting_correction:
			df.sort_values('Data', axis = 0, ascending = False, inplace = True)
			df.to_csv('./data_files/' + str(f), mode = 'w', index = False, header = True)
			print('corrected file (not unique / not sorted)', end = '	')
		
		#   removing space characters (otherwise it's not float)
		space_correction = False
		df = pd.read_csv('./data_files/' + str(f))
		for i in df:
			cnt = 0
			for j in df[i]:
				if type(j) == str:
					tmp = j.split(' ')
					if len(tmp) > 1:
						space_correction = True
						df.loc[cnt, i] = "".join(tmp)
					cnt += 1
		
		if space_correction:
			df.to_csv('./data_files/' + str(f), mode = 'w', index = False, header = True)
			print('corrected file (space problem)', end = '	')
			
		#   checking length
		with open(path + '/data_files/' + str(f), 'r') as tmp:
			if len(tmp.readlines()) < 100:
				too_short.append(f[0:3])
				print('too short', end = '	')
				
		print()
		
	
	print()	
	if(len(too_short) > 0):
		print('too short:')
		print(too_short)
		for x in too_short:
			try:
				with open(path + '/info_files/' + str(x) + '.info', 'r') as tmp:
					print(tmp.readlines()[0])
			except:
				print('no such file: ./info_files/' + str(x) + '.info')
	else:
		print('All files has a reasonable length')
				
	
if __name__ == "__main__":
	main()
