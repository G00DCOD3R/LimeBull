# Traddex

scripts used

### analize.py
stock analizing

### web_scrap_data.py
getting historical data about stocks

now scraping of 1 stock takes approximately 20 seconds (30 finished in ~10m)
have a few modes for this script, 

## Usage

### Manual mode
```
python3 web_scrap_data.py
```
if something crashes, then it's your responsibility to notice that and change which prefix of urls are completed (more information is in code's comments)

### Automated mode
```
python3 web_scrap_data.py 1
```
**if you will use this script, then most likely you have to run**
```
time python3 automated_download.py
```
instead of the first one, because the second actually manages this automated process
(you don't have to worry about anything)


### Give URLS mode
```
python3 web_scrap_data.py 2 < FILE_WITH_URLS
```
this does the same what Manual mode, but scraps only specific urls 

urls in FILE_WITH_URLS have to be separated with '\n'

**how do I get those urls?**

either copy them, or use /info_files/XYZ.info to take url of XYZ stock

note that running check_data.py will automaticly generate a list of urls which you have to fix


## check_data.py

```
python3 check_data.py
```

now it's only checking whether file is too short (less than 100 days)

moreover, as mentioned before, it generates a list of urls which you have to fix (web_scrap_data.py in Given URLS mode)

