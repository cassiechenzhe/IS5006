import random
import time
from threading import Thread, Lock

import numpy

from constants import tick_time, seed
from google_ads import GoogleAds
from market import Market
from twitter import Twitter

random.seed(seed)


class Customer(object):
    def __init__(self, name, wallet, products_list, tolerance=0.5):
        self.name, self.wallet, self.tolerance = name, wallet, tolerance

        # Register the user with google ads
        GoogleAds.register_user(self)

        # ad space stores all the adverts consumed by this user
        self.ad_space = []
        # stores all the bought products
        self.owned_products = []

        # the total product list, same as seller side
        self.products_list = products_list

        # product correlation factor matrix
        self.products_matrix = \
                  [[1, 0.7, 0.3, 0.6, 0.7, 0.5, 0.9, 0.7, 0.3],
                   [0.7, 1, 0.4, 0.2, 0.5, 0.7, 0.9, 0.2, 0.1],
                   [0.3, 0.4, 1, 0.8, 0.9, 0.1, 0.4, 0.5, 0.3],
                   [0.6, 0.2, 0.8, 1, 0.9, 0.5, 0.4, 0.7, 0.4],
                   [0.7, 0.2, 0.8, 1, 1, 0.5, 0.4, 0.7, 0.4],
                   [0.5, 0.2, 0.8, 1, 0.9, 1, 0.4, 0.7, 0.4],
                   [0.9, 0.2, 0.8, 1, 0.9, 0.5, 1, 0.7, 0.4],
                   [0.7, 0.2, 0.8, 1, 0.9, 0.5, 0.4, 1, 0.4],
                   [0.3, 0.2, 0.8, 1, 0.9, 0.5, 0.4, 0.7, 1]
                   ]

        # flag to stop thread
        self.STOP = False

        # regulate synchronisation
        self.lock = Lock()

        # start this user in separate thread
        self.thread = Thread(name=name, target=self.loop)
        self.thread.start()

    # View the advert to this consumer. The advert is appended to the ad_space
    def view_advert(self, product):
        """
        Add product into advertisement space to customer; lock thread to avoid other thread changing ad_space
        :param product: product class
        :return: none
        """
        self.lock.acquire()
        self.ad_space.append(product)
        self.lock.release()

    def buy(self, product_list):
        """
        Consumer decided to buy a 'product'.
        :param product_list: list of products
        :return: none
        """
        # if not enough money in wallet, don't proceed
        total_price = sum(product.price for product in product_list)
        if self.wallet < total_price:
            return

        # purchase the product from market
        if Market.buy(self, product_list):
            # add product to the owned products list
            for product in product_list:
                self.owned_products.append(product)

    def deduct(self, money):
        """
        money is deducted from user's wallet when purchase is completed
        :param money: money, i.e product price
        :return: none
        """
        self.wallet -= money

    def tweet(self, product, sentiment):
        """
        User expresses his sentiment about the product on twitter
        :param product: product
        :param sentiment: user sentiment, positive or negative
        :return: none
        """
        Twitter.post(self, product, sentiment)

    def loop(self):
        """
        Loop function to keep the simulation going
        :return: none
        """
        while not self.STOP:
            self.tick()
            time.sleep(tick_time)

    def tick(self):
        """
        one timestep in the simulation world
        :return: none
        """
        self.lock.acquire()
        
        current_list = self.owned_products
        purchased_products = []
        # user looks at all the adverts in his ad_space
        if len(self.ad_space) > 0:
            for product in self.ad_space:

                # user checks the reviews about the product on twitter
                tweets = numpy.asarray(Twitter.get_latest_tweets(product, 20))
                user_sentiment = 1 if len(tweets) == 0 else (tweets == 'POSITIVE').mean()
                
                # quality insentive customers still buy if sentiment is lower than tolerance but low probability
                if user_sentiment < self.tolerance and random.random() < 0.1:
                    purchased_products.append(product)
                
                elif user_sentiment >= self.tolerance:
                    if product in current_list and random.random() < 0.3:
                        #self.buy(product)
                        purchased_products.append(product)
                    elif product not in current_list and random.random() < 0.9:
                        product_id = self.products_list.index(product)
                        if len(current_list) > 0:
                            for item in current_list:
                                item_id = self.products_list.index(item)
                                #print("This is the current own item id:", item_id)
                                if self.products_matrix[product_id][item_id] > 0.2:
                                    purchased_products.append(product)
                        else:
                            purchased_products.append(product)
        self.buy(purchased_products)
        # remove the adverts from ad_space
        self.ad_space = []
        
        self.lock.release()
        # with some chance, the user may tweet about the product
        if random.random() < 0.5 and len(self.owned_products) > 0:
            # he may choose any random product
            product = random.choice(list(self.owned_products))

            # sentiment in positive if the quality is higher than the tolerance
            sentiment = 'POSITIVE' if self.tolerance < product.quality else 'NEGATIVE'

            # tweet sent
            self.tweet(product, sentiment)

    def kill(self):
        """
        set the flag to True and wait for thread to join
        :return: none
        """
        self.STOP = True
        self.thread.join(timeout=0)

    def __str__(self):
        return self.name
