Web Scraper built using python Scrapy
For extracting mobile phone specifications from gsmarena.com

1. Scraped 10144 devices and their specifications from 10144 pages containing the model specifications, 116 brand pages containing multi-sub pages for the models listing by each brand, and 1 page containing all the brands which was the entry point for the Web Spider.
2. Total run time of over 48 hours so as to not overload the server and prevent banning.


Challenges faced -
1. Overloading target server, hence used the library scrapy-rotating-proxies with a list of a number of free open proxies obtained online.
2. Lack of understanding in CONCURRENT_REQUESTS settings along with the proxies, so total run time could probably have been reduced.
3. Improper handling of target webpage html, resulting in some mismatch between column and data.

To Do - 
1. Data cleaning
2. Data Analysis
3. Setup automation for monitoring any new additions / changes in the site
