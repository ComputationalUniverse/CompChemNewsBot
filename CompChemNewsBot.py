# importing modules
import feedparser
from bs4 import BeautifulSoup
import tweepy
from decouple import config
import logging
import datetime
import random

# url for collecting news
url = "http://news.google.com/news?q=computational+chemistry&hl=en-US&sort=date&gl=US&num=100&output=rss"

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

class ParseFeed():

    def __init__(self, url):
        self.feed_url = url

    def clean(self, html):
        '''
        Getting the text from html and doing some cleaning
        '''
        soup = BeautifulSoup(html)
        text = soup.get_text()
        text = text.replace('\xa0', ' ')
        return text

    def follow_back(self, api):
        '''
        Following back to those users who are retweeting
        '''
        # getting the retweeters of latest tweet
        latest_tweet_id = (api.user_timeline(count=1)[0]).id
        retweets_list = api.retweets(latest_tweet_id)
        user_name_list = [
            retweet.user.id for retweet in retweets_list]
        
        # getting the friendlist
        friend_list = [friend for friend in api.friends(
            user_id="CompChemNewsBot")]
        friend_final_list = [friend.id for friend in friend_list]

        # removing the already followed users
        final_list = [
            elem for elem in user_name_list if elem not in friend_final_list]

        # in case no new user to follow
        if final_list == []:
            logger.info(
                f"No new user found at: {str(datetime.datetime.now())}\n\t\t\t\t\t\t******\t\t\t\t\t\t")

        # new user found and following the user
        else:
            for user in final_list:
                try:
                    api.create_friendship(user_id=user)
                    logger.info(
                        f"{user} UserID followed back at : {str(datetime.datetime.now())}\n\t\t\t\t\t\t******\t\t\t\t\t\t")
                except Exception as e:
                    logger.info(
                        f"Can't be followed back at : {str(datetime.datetime.now())} due to {e} error\n\t\t\t\t\t\t******\t\t\t\t\t\t")

    def tweet(self, text_list, url_list):
        '''
        Posting the news in the twitter and logging the data (First news of the list will be posted: One can modify by using random function)
        '''
        while True:
            choice = random.choice(range(len(text_list)+1))
            try:
                api.update_status(f"@aritraroy24 #compchem #news #update #science #chemistry #quantum\n𝙏𝙊𝘿𝘼𝙔'𝙎 𝙐𝙋𝘿𝘼𝙏𝙀: {text_list[choice]}\n{url_list[choice]}")
                logger.info(
                    f"Tweet done at : {str(datetime.datetime.now())} === {text_list[choice]} === {url_list[choice]}\n\n\n")
                break

            except Exception as e:
                logger.info(
                    f"Tweet can't be done at : {str(datetime.datetime.now())} due to {e} error\n\n\n")

                if "duplicate" in str(e):
                    continue
                

    def parse(self):
        '''
        Parsing URL, and collecting descriptions and URLs of the news of which the character length of the tweet is in between 100 and 200
        '''
        text_list = []
        url_list = []
        feeds = feedparser.parse(self.feed_url).entries
        for f in feeds:
            text = self.clean(f.get("description"))
            url = f.get("link")
            count = sum((text[i] != ' ') for i in range(len(text)))
            if 100 < count < 200:
                text_list.append(text)
                url_list.append(url)
        self.follow_back(api)
        self.tweet(text_list, url_list)

feed = ParseFeed(url)
feed.parse()
