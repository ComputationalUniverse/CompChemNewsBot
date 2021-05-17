# importing modules
import feedparser
from bs4 import BeautifulSoup
import tweepy
from decouple import config
import logging
import datetime
import random

# url for collecting news
url = "http://news.google.com/news?q=computational+chemistry+when:1d&hl=en-IN&gl=IN&ceid=IN:en&output=rss"

# logging config
logging.basicConfig(level=logging.INFO, filename='data.txt',)
logger = logging.getLogger()

# Keys
CONSUMER_KEY = config('Consumer_Key')
CONSUMER_SECRET_KEY = config('Consumer_Secret_Key')
ACCESS_TOKEN = config('Access_Token')
ACCESS_TOKEN_SECRET = config('Access_Token_Secret')

# Authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


