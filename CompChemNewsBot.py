# importing modules
import feedparser
from bs4 import BeautifulSoup
import tweepy
from decouple import config
import logging
import datetime

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
        # removing news already tweeted
        file_name = "tweets.txt"
        with open(file_name, "r") as file:
            tweet_list = file.readlines()
        tweet_list = [x.strip() for x in tweet_list] 
        for tweet in tweet_list:
            for text, url in zip(text_list, url_list):
                if text == tweet:
                     text_list.remove(text)
                     url_list.remove(url)

        # tweeting the fast news from the modified newslist
        for text in text_list:
            i = 0
            try:
                with open(file_name, "a") as file:
                    file.write(f"{text}\n\n")
                api.update_status(
                    f"@aritraroy24 #compchem #news #update #science #chemistry #quantum\n𝙏𝙊𝘿𝘼𝙔'𝙎 𝙐𝙋𝘿𝘼𝙏𝙀: {text_list[i]}\n{url_list[i]}")
                logger.info(
                    f"Tweet done at : {str(datetime.datetime.now())} === {text_list[i]} === {url_list[i]}\n\n\n")
                i += 1
                break

            except Exception as e:
                logger.info(
                    f"Tweet can't be done at : {str(datetime.datetime.now())} due to {e} error\n\n\n")

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
            if count < 150:
                text_list.append(text)
                url_list.append(url)
        self.follow_back(api)
        self.tweet(text_list, url_list)


feed = ParseFeed(url)
feed.parse()