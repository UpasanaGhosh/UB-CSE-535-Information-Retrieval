import tweepy
import json
from datetime import datetime, timedelta
import re
import demoji
import datetime
from dateutil.parser import parse

# inputfile = "yadavakhileshReply"
# country = "India"
null = None


def connect_to_twitter():
    consumer_key = "iXmQt84QTdU4uVajypugSsPqV"
    consumer_secret = "GeTYh729O5dgBYytHxwR8Q4vImth5htFVqb4zbV65792mLPpeb"
    access_key = "1066216367504875520-X3RwzrhlbN1CQE3GefdsJXR6ns6uaa"
    access_secret = "0tWzmtZlzgs5OgsaMf235tllns23LhLCcWHcOG1sswB0F"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    return api


def remove_hashtags(string):
    string_array = string.split(' ')
    output_string = ''
    op_list = []
    for word in range(0, len(string_array)):
        try:
            if string_array[word].startswith('#') or '#' in string_array[word]:
                continue
            else:
                if string_array[word] not in op_list:
                    op_list.append(string_array[word])
        except IndexError as e:
            break
    for w in op_list:
        output_string = output_string + ' ' + w
    return output_string


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    # list_emoji=demoji.findall(string)
    return emoji_pattern.sub(r'', string)


def remove_url(string):
    # text = re.sub(r'^http\s+?:\/\/.*[\r\n]*', '', string, flags=re.MULTILINE)
    text = re.sub(
        r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''',
        " ", string)
    return text


def get_emoji_list(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    emoticons_dict = demoji.findall(string)
    if emoticons_dict is not null:
        emo_list = []
        for emo in emoticons_dict.keys():
            emo_list.append(emo)
    return emo_list


def remove_user_mentions(string):
    string_array = string.split(' ')
    output_string = ''
    op_list = []
    for word in range(0, len(string_array)):
        try:
            if string_array[word].startswith('@') or '@' in string_array[word]:
                continue
            else:
                if string_array[word] not in op_list:
                    op_list.append(string_array[word])
        except IndexError as e:
            break
    for w in op_list:
        output_string = output_string + ' ' + w
    return output_string


# trim list to 'count' replies
def trim_replies_list(tweet_dict_list):
    final_list = []
    for tweet_id in tweet_dict_list.keys():
        replies_list = tweet_dict_list[tweet_id]
        if len(replies_list) > 60:
            final_list = replies_list[0:60]
        else:
            final_list = replies_list
        tweet_dict_list[tweet_id] = final_list
    return tweet_dict_list


# consolidate reply tweets to a single list
def consolidate_reply_tweets(tweet_dictionary):
    # consolidating all reply tweets into one master list
    tweet_list = []
    for tweet_id in tweet_dictionary.keys():
        for tweet in tweet_dictionary[tweet_id]:
            tweet_list.append(tweet)
    return tweet_list


def modify_fields_json(tweets_json, tweet_type):
    modified_tweets_list = []
    for tweet in tweets_json:
        filtered_text = ''
        modified_tweet = tweet
        if tweet_type == 'reply':
            modified_tweet['poi_name'] = tweet['in_reply_to_screen_name']
            modified_tweet['poi_id'] = tweet['in_reply_to_user_id_str']

        else:
            modified_tweet['poi_name'] = tweet['user']['screen_name']
            modified_tweet['poi_id'] = tweet['user']['id_str']

        modified_tweet['verified'] = tweet['user']['verified']
        modified_tweet['country'] = country  # hardcoded from top
        modified_tweet['replied_to_tweet_id'] = tweet['in_reply_to_status_id_str']
        if tweet['in_reply_to_status_id_str'] is null:  # check if None = null
            modified_tweet['replied_to_user_id'] = null
            modified_tweet['reply_text'] = null
        else:
            modified_tweet['replied_to_user_id'] = tweet['in_reply_to_user_id_str']
            modified_tweet['reply_text'] = tweet['full_text']
            # have to convert date
        modified_tweet['tweet_text'] = tweet['full_text']
        modified_tweet['tweet_lang'] = tweet['lang']
        temp_text = tweet['full_text']
        filtered_text_without_emoji = remove_emoji(temp_text)
        filtered_text_without_hashtags = remove_hashtags(filtered_text_without_emoji)
        filtered_text_without_mentions = remove_url(filtered_text_without_hashtags)
        filtered_text = remove_user_mentions(filtered_text_without_mentions)
        if tweet['lang'] == "hi":
            modified_tweet['text_hi'] = filtered_text
        elif tweet['lang'] == "en":
            modified_tweet['text_en'] = filtered_text
        elif tweet['lang'] == "pt":
            modified_tweet["text_pt"] = filtered_text

        hashtags = []
        if len(tweet['entities']['hashtags']) != 0:
            for hashtag in tweet['entities']['hashtags']:
                hashtags.append(hashtag['text'])

        modified_tweet['hashtags'] = hashtags
        user_list = []
        for user in tweet['entities']['user_mentions']:
            user_list.append(user['screen_name'])
        modified_tweet['mentions'] = user_list
        modified_tweet['tweet_urls'] = tweet['entities']['urls']
        emo_list = get_emoji_list(tweet['full_text'])
        modified_tweet['tweet_emoticons'] = emo_list
        date_str = parse(tweet['created_at'])
        time_obj = date_str.replace(second=0, microsecond=0, minute=0, hour=date_str.hour) + timedelta(
            hours=date_str.minute // 30)
        date_str = datetime.datetime.strftime(time_obj, '%Y-%m-%d %H:%M:%S')
        modified_tweet['tweet_date'] = date_str
        modified_tweet['tweet_loc'] = tweet['coordinates']

        modified_tweets_list.append(modified_tweet)
    return modified_tweets_list


def get_tweets_from_files(inputfile):
    f = open('final/' + inputfile + '.json', "r")
    tweets = f.read()
    tweets_json = json.loads(tweets)
    return tweets_json


def store_tweets(alltweets, filename):
    op = json.dumps(alltweets)
    with open('final/modified/' + filename + '.json', 'w+') as f1:
        f1.write(op)


def trim_tweets(tweets, inputfile):
    tweet_id_list_with_less_than20_replies = []
    final_tweet_list = []
    repliesOriginal = get_tweets_from_files(inputfile + "Reply")
    for tweet_id in repliesOriginal.keys():
        replies_list = repliesOriginal[tweet_id]
        if len(replies_list) < 20:
            tweet_id_list_with_less_than20_replies.append(tweet_id)

    for tweet in tweets:
        if tweet['id_str'] not in tweet_id_list_with_less_than20_replies:
            final_tweet_list.append(tweet)
    return final_tweet_list


def read_replies_from_twarc(filename):
    tweets = []
    with open(filename, 'a') as data_file:
        json_object = json.loads(data_file)


if __name__ == '__main__':

    # read_replies_from_twarc('AdamSchiff/1170085840858599424.json')
    '''
        poi_lists = [
        {'country': 'India', 'poi_list': ['AmitShahReply', 'VasundharaBJPReply', 'yadavakhileshReply', 'NitishKumarReply', 'RahulGandhiReply']},
        {'country': 'Brazil',
         'poi_list': ['BolsonaroSPReply', 'dilmabrReply', 'jairbolsonaroReply', 'majorolimpioReply', 'MajorVitorHugoReply']},
        {'country': 'USA', 'poi_list': ['NYGovCuomoReply', 'OprahReply', 'RepAdamSchiffReply', 'HillaryClintonReply', 'JoeBidenReply']}]
    '''


    poi_lists = [
        {'country': 'India',
         'poi_list': ['AmitShahKeywords']},
        {'country': 'USA',
         'poi_list': ['OprahKeywords', 'HillaryClintonKeywords', 'JoeBidenKeywords']}]

    for poi_list in poi_lists:
        country = poi_list['country']
        for poi in poi_list['poi_list']:
            inputfile = poi
            tweets = get_tweets_from_files(inputfile)
            modified_tweets = []
            tweet_type = ''
            if inputfile.find('Reply') > 0:
                # call only for reply tweets
                tweet_type = 'reply'
                trimmed_replies = trim_replies_list(tweets)
                replied_tweets = consolidate_reply_tweets(trimmed_replies)
                modified_tweets = modify_fields_json(replied_tweets, tweet_type)
            elif inputfile.find('Keywords') > 0:
                tweet_type = 'reply'
                modified_tweets = modify_fields_json(tweets, tweet_type)
            else:
                tweet_type = 'tweet'
                #trimmed_tweets = trim_tweets(tweets, poi)
                modified_tweets = modify_fields_json(tweets, tweet_type)

            store_tweets(modified_tweets, inputfile + 'FINAL')
