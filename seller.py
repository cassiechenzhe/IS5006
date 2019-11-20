import time
from threading import Lock, Thread

import numpy

from constants import tick_time
from google_ads import GoogleAds
from market import Market
from twitter import Twitter


class Seller(object):

    def __init__(self, name, product, wallet):
        self.name = name
        self.product = product
        self.wallet = wallet

        # register the seller in market
        Market.register_seller(self, product)

        # metrics tracker
        self.sales_history = []
        self.revenue_history = []
        self.profit_history = []
        self.expense_history = [0]
        self.sentiment_history = []
        self.item_sold = 0

        # Flag for thread
        self.STOP = False

        self.lock = Lock()

        # start this seller in separate thread
        self.thread = Thread(name=name, target=self.loop)
        self.thread.start()

    def loop(self):
        while not self.STOP:
            self.tick()
            time.sleep(tick_time)

    # if an item is sold, add it to the database
    def sold(self):
        self.lock.acquire()
        self.item_sold += 1
        self.lock.release()

    # one timestep in the simulation world
    def tick(self):
        self.lock.acquire()

        # append the sales record to the history
        self.sales_history.append(self.item_sold)

        # reset the sales counter
        self.item_sold = 0

        self.lock.release()

        # Calculate the metrics for previous tick and add to tracker
        self.revenue_history.append(self.sales_history[-1] * self.product.price)
        self.profit_history.append(self.revenue_history[-1] - self.expense_history[-1])
        self.sentiment_history.append(self.user_sentiment())

        # add the profit to seller's wallet
        self.wallet += self.my_profit(True)

        # choose what to do for next timestep
        advert_type, scale = self.CEO()

        # ANSWER a. print data to show progress
        print('Revenue in previous quarter:', self.my_revenue(True))
        print('Expenses in previous quarter:', self.my_expenses(True))
        print('Profit in previous quarter:', self.my_profit(True))
        print('\nStrategy for next quarter \nAdvert Type: {}, scale: {}\n\n'.format(advert_type, scale))

        # perform the actions and view the expense
        self.expense_history.append(GoogleAds.post_advertisement(self, self.product, advert_type, scale))

    # calculates the total revenue. Gives the revenue in last tick if latest_only = True
    def my_revenue(self, latest_only=False):
        revenue = self.revenue_history[-1] if latest_only else numpy.sum(self.revenue_history)
        return revenue

    # calculates the total revenue. Gives the revenue in last tick if latest_only = True
    def my_expenses(self, latest_only=False):
        bill = self.expense_history[-1] if latest_only else numpy.sum(self.expense_history)
        return bill

    # calculates the total revenue. Gives the revenue in last tick if latest_only = True
    def my_profit(self, latest_only=False):
        profit = self.profit_history[-1] if latest_only else numpy.sum(self.profit_history)
        return profit

    # calculates the user sentiment from tweets.
    def user_sentiment(self):
        tweets = numpy.asarray(Twitter.get_latest_tweets(self.product, 100))
        return 1 if len(tweets) == 0 else (tweets == 'POSITIVE').mean()

    # to stop the seller thread
    def kill(self):
        self.STOP = True
        self.thread.join()

    def __str__(self):
        return self.name

    # Cognition system that decides what to do next.
    def CEO(self):
        # WRITE YOUR INTELLIGENT CODE HERE
        # You can use following functions to make decision
        #   my_revenue
        #   my_expenses
        #   my_profit
        #   user_sentiment
        #
        # You need to return the type of advert you want to publish and at what scale
        # GoogleAds.advert_price[advert_type] gives you the rate of an advert

        advert_type = GoogleAds.ADVERT_BASIC if GoogleAds.user_coverage(self.product) < 0.5 else GoogleAds.ADVERT_TARGETED
        scale = self.wallet // GoogleAds.advert_price[advert_type] // 2 #not spending everything
        return advert_type, scale
