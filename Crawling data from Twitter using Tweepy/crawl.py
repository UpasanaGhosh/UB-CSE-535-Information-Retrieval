import tweepy
import json
import sys

consumer_key = "iXmQt84QTdU4uVajypugSsPqV"
consumer_secret = "GeTYh729O5dgBYytHxwR8Q4vImth5htFVqb4zbV65792mLPpeb"
access_key = "1066216367504875520-X3RwzrhlbN1CQE3GefdsJXR6ns6uaa"
access_secret = "0tWzmtZlzgs5OgsaMf235tllns23LhLCcWHcOG1sswB0F"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)
screen_name = "Oprah"
filenamefinal = "Oprah"


def get_all_tweets(screen_name: object):
    """
    # initialize a list to hold all the temporary tweepy Tweets
    temptweets = []
    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    # save most recent tweets
    temptweets.extend(new_tweets)

    # filtering out retweets
    for tweet in temptweets:
        if (not tweet.retweeted) and ('RT @' not in tweet.text):
            alltweets.append(tweet)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:

        print("getting tweets before %s" % (oldest))

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)

        # filtering out retweets
        #for tweet in temptweets:
            #if (not tweet.retweeted) and ('RT @' not in tweet.text):
        # save most recent tweets
        if (not tweet.retweeted) and ('RT @' not in tweet.text):
            alltweets.append(tweet)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...%s tweets downloaded so far" % (len(alltweets)))

    count = 0
    for tweet in alltweets:
        count = count + 1
    print(count)
    return alltweets
    """
    temptweets = []
    alltweets = []
    new_tweets = api.user_timeline(screen_name=screen_name, count=199)
    alltweets.extend(new_tweets)
    print(alltweets[1].id)
    oldest = alltweets[-1].id - 1
    while 0 < len(new_tweets) < 200:
        new_tweets = tweepy.Cursor(api.user_timeline, screen_name=screen_name, count=199, max_id=oldest).items(1500)
        alltweets.extend(new_tweets)
        for tweet in alltweets:
            if (not tweet.retweeted) and ('RT @' not in tweet.text):
                temptweets.append(tweet)
        oldest = alltweets[-1].id - 1
    print("Total tweets downloaded from %s are %s" % (screen_name, len(temptweets)))
    return temptweets


def store_tweets(alltweets, filename):
    file = open(filename + ".json", 'w', encoding='utf8')

    for status in alltweets:
        print(status)
        json.dump(status._json, file)
    file.close()

def get_hashtag_tweets(hashtags):
    tweets = []
    for tweet in tweepy.Cursor(api.search, q="#Oprahs2020VisionTour", result_type='recent', timeout=999999,
                               tweet_mode='extended').items(1000):
        if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
            tweets.append(tweet._json)

    return tweets

def get_replies(name):
    replies = []
    for full_tweets in tweepy.Cursor(api.user_timeline, screen_name=name, timeout=999999).items(10):
        for tweet in tweepy.Cursor(api.search, q='to:' + name).items(1000):
            if hasattr(tweet, 'in_reply_to_status_id_str'):
                if tweet.in_reply_to_status_id_str == full_tweets.id_str:
                    replies.append(tweet)

        return replies


if __name__ == '__main__':
    # pass in the username of the account you want to download
    #alltweets = get_all_tweets(screen_name)
    # replies=[]
    # replies = get_replies(name)
    # store_tweets(replies, "replies")

    # store the data into json file
    alltweets = get_hashtag_tweets('#Oprahs2020VisionTour')
    store_tweets(alltweets, filenamefinal)
