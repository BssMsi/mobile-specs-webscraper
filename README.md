# Web Scraper built using python Scrapy
## For extracting mobile phone specifications from gsmarena.com

* Scraped 10144 devices and their specifications from 10144 pages containing the model specifications, 116 brand pages containing multi-sub pages for the models listing by each brand, and 1 page containing all the brands which was the entry point for the Web Spider.
* Total run time of over 48 hours so as to not overload the server and prevent banning.

### Challenges faced -
1. Overloading target server, hence used the library scrapy-rotating-proxies with a list of a number of free open proxies obtained online.
2. Lack of understanding in CONCURRENT_REQUESTS settings along with the proxies, so total run time could probably have been reduced.
3. Improper handling of target webpage html, resulting in some mismatch between column and data.

### Guide to Files - 
* files/specs_extracted.csv - extracted specifications into separate columns
* files/gsmarena_data.csv - **raw data** scraped directly containing the specifications as nested dictionaries under single column
* files/gsmarena_brands.csv - **raw data** containing all the brands and number of models in each brand according to the site
* analysis.ipynb - some data cleaning and extracting the specifications into columns
* files/visited_models.txt - all the visited model specification urls

### To Do - 
1. Data cleaning
2. Data Analysis
3. Setup automation for monitoring any new additions / changes in the site
