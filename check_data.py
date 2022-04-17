import os, sys

def main():
	path = '/home/tymon/Programy/C++/gh/tradde'
	files = os.listdir(path + '/data_files')
	too_short = []
	for f in files:
		if (f[0] > 'Z'):
			continue
		with open(path + '/data_files/' + str(f), 'r') as tmp:
			if len(tmp.readlines()) < 100:
				too_short.append(f[0:3])
	if(len(too_short) > 0):
		print('too short:')
		print(too_short)
		for x in too_short:
			with open(path + '/info_files/' + str(x) + '.info', 'r') as tmp:
				print(tmp.readlines()[0])
	else:
		print('All files has a reasonable length')
				
	
if __name__ == "__main__":
	main()
