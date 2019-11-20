import time
from threading import Lock, Thread

import numpy

from constants import tick_time
from google_ads import GoogleAds
from market import Market
from twitter import Twitter
import sheet_api


class Seller(object):

    def __init__(self, name, products_list, wallet):

        self.name = name
        # Each seller can sell multiple products, products_list is
        self.products_list = []
        # self.product = product
        self.wallet = wallet

        # register the seller with each product it owns in market
        if products_list is not None:
            for product in products_list:
                Market.register_seller(self, product)

        # metrics tracker: a list of dictionary with product as key
        self.inventory = [{key: 1000 for key in products_list}]  # assume inventory starts with 1000 items
        self.sales_history = [{key: 0 for key in products_list}]
        self.revenue_history = [{key: 0 for key in products_list}]
        self.profit_history = [{key: 0 for key in products_list}]
        self.expense_history = [{key: 0 for key in products_list}]
        self.sentiment_history = [{key: 0 for key in products_list}]

        # total items of all products sold by seller
        self.item_sold = 0

        # qtr number
        self.qtr = 0

        # google sheet to store records
        self.worksheet = sheet_api.workbook.worksheet(self.name)

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

        # record timestamp/quarter number
        self.qtr += 1

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

        # write into google worksheet
        self.worksheet.update_acell(str('A') + str(self.qtr + 1), self.name)
        self.worksheet.update_acell(str('B') + str(self.qtr + 1), self.qtr)
        self.worksheet.update_acell(str('C') + str(self.qtr + 1), self.my_revenue(True))
        self.worksheet.update_acell(str('D') + str(self.qtr + 1), self.my_expenses(True))
        self.worksheet.update_acell(str('E') + str(self.qtr + 1), self.my_profit(True))
        self.worksheet.update_acell(str('F') + str(self.qtr + 1),
                                    'Strategy for next quarter Advert Type:{}, scale: {}'.format(advert_type, scale))

        self.lock.release()

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
        """
        Choose advertisement types and scales based on sales, revenue and user_coverage.
        If revenue is below average or user_coverage is less than target, choose targeted ads, otherwise choose basic ads.
        Set total advertisement budget less than a percentage of revenue, to avoid bankrupt
        Scale (number of ads to put) equals to budget divided by advert price.

        :return: the type of advert you want to publish and at what scale for each product
        """
        advert_type = GoogleAds.ADVERT_BASIC if GoogleAds.user_coverage(
            self.product) < 0.5 else GoogleAds.ADVERT_TARGETED
        scale = self.wallet // GoogleAds.advert_price[advert_type] // 2  # not spending everything
        return advert_type, scale
