from threading import Lock
from collections import defaultdict


class Twitter(object):
    # dictionary to store tweets
    feed = defaultdict(list)
    lock = Lock()

    # Called by the user to tweet something
    @staticmethod
    def post(user, product, tweet):
        Twitter.feed[product].append((user, tweet))

    # returns the latest tweet about a product.
    @staticmethod
    def get_latest_tweets(product, n):
        Twitter.lock.acquire()
        latest_tweets = [tweet for user, tweet in Twitter.feed[product][-n:]]
        Twitter.lock.release()
        return latest_tweets
