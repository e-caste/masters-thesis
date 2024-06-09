## OpenHPI Lectures Dataset

To use this code, run the 4 numbered scripts in order. They will:
1. get all available course URLs from the OpenHPI API and then scrape the course's data from the OpenHPI platform using Selenium and its webdriver for Firefox (an OpenHPI account is needed: create one at https://open.hpi.de/account/new and paste your e-mail and password in common.py) -- this will also enroll your account into all available courses in English on OpenHPI
2. print some stats about the scraped data
3. download transcripts and optionally videos, slides, and audios for all lectures
4. fix the downloaded transcripts and remove duplicate courses