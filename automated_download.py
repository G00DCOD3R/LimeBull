import os, time

#   this is program which automaticly runs web_scrap_data.py
#   use it if you want to download all that data without any supervision
#   e.g. leave for a few hours, without any need to look whether everything is ok
#   it's mainly used because some wifi problems can kill web_scrap script, thus terminating downloading process


def main():
	name = 'TEMP_web_scrap_latest'
	os.system('touch ' + str(name))
	with open(name, 'w') as tmp_file:
		tmp_file.write("-1\n")
	while True:
		with open(name, 'r') as tmp_file:
			if(tmp_file.readlines()[0] == 'Done\n'):
				break
			else:
				os.system('killall -s SIGKILL chromedriver')
				os.system('killall -s SIGKILL chrome')
				os.system('clear')
				os.system('python3 web_scrap_data.py 1')
			time.sleep(1)
	print("THE END OF DOWNLOADING\ndoing check")
	os.system('rm ' + str(name))
	os.system('python3 check_data.py')

if __name__ == "__main__": 
	main()
