import tweepy
import json
import time

screen_name = "jairbolsonaro"
filenamefinal = "jairbolsonaro"
poi_id = "1339835893"
id = "1168552808238313472"

'''
Utility method to connect to the Tweepy APIs
'''
def connect_to_twitter():
    consumer_key = "<TWEEPY CONSUMER KEY>"
    consumer_secret = "<TWEEPY CONSUMER SECRET>"
    access_key = "<TWEEPY ACCESS TOKEN KEY>"
    access_secret = "<TWEEPY ACCESS TOKEN SECRET>"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    return api

'''
Method to get all tweets for a particular POI (Person Of Interest) filtering out the retweets
'''
def get_all_tweets(screen_name: object):
    api = connect_to_twitter()
    temptweets = []
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=screen_name, result_type='recent', timeout=999999,
                               tweet_mode='extended').items(2000):
        if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
            temptweets.append(tweet._json)
            # print(tweet)
    return temptweets

'''
Method to get tweets against a list of hashtags for a particular POI
'''
def get_hashtag_tweets(hashtags, poi_id):
    api = connect_to_twitter()
    '''
    while(hashtag in hashtags):
        query_stry = hashtag + " or "
    '''
    tweets = []
    RT_count = 0
    tweet_cursor = tweepy.Cursor(api.search, q=hashtags[0] or hashtags[1] or hashtags[2], result_type='recent', timeout=999999, tweet_mode='extended').items(1000)
    count = 0
    while count <= 100:
        tweet = tweet_cursor.next()
        try:
            if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
                user = tweet._json['user']
                if user['id_str'] != poi_id:
                    tweets.append(tweet._json)
                    count = count + 1
        except tweepy.RateLimitError as e:
            print("--------------- Rate Limit Exceeded --------------")
            print(e)
            time.sleep(60 * 15)
            print("--------------- Start Processing --------------")
            continue

        except tweepy.TweepError as e:
            print("--------------- Tweep Error --------------")
            print(e)
            time.sleep(60 * 15)
            print("--------------- Start Processing --------------")
            continue

        except Exception as e:
            print(e)
            break

    return tweets


def store_tweets(alltweets, filename):
    op = json.dumps(alltweets)
    with open(filename + ".json", 'w+') as f1:
        f1.write(op)


def check_tweet_replies_length(tweet_replies_dict):
    cond_fulfilled = False
    for tweet_id in tweet_replies_dict.keys():
        if len(tweet_replies_dict[tweet_id]) >= 150:
            cond_fulfilled = True
        else:
            cond_fulfilled = False
            break
    return cond_fulfilled

'''
To fetch the replies for a list of tweets, we need to have the tweets in place.
The tweets should be present in a folder 'tweets' and the filename should be passed
to get_replies while making the call. A timeframe of five days is considered to get the replies.
The dates need to be updated while making the call to set the proper timeframe.
'''
def get_replies(filename):
    api = connect_to_twitter()

    f = open('tweets/' + filename + '.json', "r")
    tweets = f.read()
    tweets_json = json.loads(tweets)
    f.close()
    tweets_for_reply = []
    # print(tweets_json)

    for tweet in tweets_json:
        t = tweet['created_at']
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(t, '%a %b %d %H:%M:%S +0000 %Y'))
        if '2019-09-02 00:00' <= ts < '2019-09-07 00:00':
            tweets_for_reply.append(str(tweet['id']))
    # print(tweets_for_reply)

    tweets_for_reply.sort(reverse=True)
    replies = {}
    # print("tweet count for reply: %d", count)

    count = 0
    for t_id in tweets_for_reply:
        if count == 0:
            tweet_replies = tweepy.Cursor(api.search, q='to:{} filter:replies'.format(screen_name), sinceId=t_id,
                                          tweet_mode='extended').items(300)
        else:
            tweet_replies = tweepy.Cursor(api.search, q='to:{} filter:replies'.format(screen_name), sinceId=t_id,
                                          max_id=prev - 1, tweet_mode='extended').items(300)

        while True:
            try:
                reply = tweet_replies.next()
                if hasattr(reply, 'in_reply_to_status_id_str'):
                    if reply.in_reply_to_status_id_str in replies:
                        if check_tweet_replies_length(replies) or len(replies[t_id]) >= 100:
                            break
                        replies[reply.in_reply_to_status_id_str].append(reply._json)
                    elif reply.in_reply_to_status_id_str in tweets_for_reply:
                        replies[reply.in_reply_to_status_id_str] = [reply._json]

            except tweepy.RateLimitError as e:
                print("--------------- Rate Limit Exceeded --------------")
                print(e)
                time.sleep(60 * 15)
                print("--------------- Start Processing --------------")
                continue

            except tweepy.TweepError as e:
                print("--------------- Tweep Error --------------")
                print(e)
                time.sleep(60 * 15)
                print("--------------- Start Processing --------------")
                continue

            except Exception as e:
                print(e)
                break

        count = count + 1
        prev = int(t_id)
        if check_tweet_replies_length(replies):
            break

    # print(replies)
    return replies


if __name__ == '__main__':
    # pass in the username of the account you want to download
    all_tweets = get_all_tweets(screen_name)

    # store the data into json file
    store_tweets(all_tweets, filenamefinal)

    '''
    replies = get_replies(screen_name)
    for reply in replies.keys():
        print(reply + ": %d", len(replies[reply]))
    
    tweets = get_hashtag_tweets(["#hillaryclinton", "#impeachtrump", "#democrats"], "1339835893")
    store_tweets(tweets, filenamefinal + "Keywords")
    '''
