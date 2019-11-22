import time
from threading import Lock, Thread

import numpy

from constants import tick_time
from google_ads import GoogleAds
from market import Market
from twitter import Twitter
#import sheet_api


class Seller(object):

    def __init__(self, name, products_list, wallet):
        """
        A class to represent the seller
        :param name: seller name string, eg. apple
        :param products_list: list of products sold by the seller
        :param wallet: total money owned by the seller
        """
        self.name = name
        # Each seller can sell multiple products in products_list
        self.products_list = []
        # self.product = product
        self.wallet = wallet

        # register the seller with each product it owns in market
        if products_list is not None:
            for product in products_list:
                Market.register_seller(self, product)

        # metrics tracker:
        # item_sold is total number of items of each product sold by seller.
        # A dictionary with each product as key and value is no. of items sold.eg.{iphone: 0, airpods: 0}
        self.item_sold = {key: 0 for key in products_list}

        # inventory is a list of dictionary with product as key and inventory number as value for each quarter
        # assume initial inventory is 1000 items for each product. Eg.[{iphone: 1000, airpods: 1000}]
        self.inventory = [{key: 1000 for key in products_list}]

        # sales, revenue, profit, expense and sentiment history start with zero for each product
        # Eg.[{iphone: 0, airpods: 0}]
        self.sales_history = [{key: 0 for key in products_list}]
        self.revenue_history = [{key: 0 for key in products_list}]
        self.profit_history = [{key: 0 for key in products_list}]
        self.expense_history = [{key: 0 for key in products_list}]
        self.sentiment_history = [{key: 0 for key in products_list}]

        # qtr number
        self.qtr = 0

        # google sheet to store records
        #self.worksheet = sheet_api.workbook.worksheet(self.name)

        # Flag for thread
        self.STOP = False

        self.lock = Lock()

        # start this seller in separate thread
        self.thread = Thread(name=name, target=self.loop)
        self.thread.start()

    def loop(self):
        """
        tick time for seller, one tick represent one quarter
        :return: none
        """
        while not self.STOP:
            self.tick()
            time.sleep(tick_time)

    def sold(self, product):
        """
        Add to the database when an item is sold
        :param product: product sold by the seller
        :return: none
        """
        self.lock.acquire()
        self.item_sold[product] += 1
        self.lock.release()

    def tick(self):
        """
        Actions to do in one time step in the simulation world:
        1. record sales history of number of items sold for each product
        2. calculate the metrics for previous tick and add to tracker, like revenue, expense, profit, user sentiment
        3. decide advertising type in next step by calling CEO function
        :return: none
        """
        # lock time to avoid actions overlap
        self.lock.acquire()

        # record timestamp/quarter number
        self.qtr += 1
        
        self.record_metric()

        # add the profit to seller's wallet
        self.wallet += self.my_profit(True)

        # reset the sales counter
        self.item_sold.fromkeys(self.item_sold, 0)
        
        # adjust price for next time step
        self.adjust_price()

        # choose advertisement strategy for next time step
        advert_type, scale = self.CEO()
        
        # print data to show progress
        print('\n\nSeller: ', self.name)
        print('Revenue in previous quarter:', self.my_revenue(True))
        print('Expenses in previous quarter:', self.my_expenses(True))
        print('Profit in previous quarter:', self.my_profit(True))
        #print('\nStrategy for next quarter \nProduct: {}, Advert Type: {}, scale: {}\n\n'.format(product.name, advert_type[product], scale[product]) for product in self.products_list)

        # write into google worksheet
#        self.worksheet.update_acell(str('A') + str(self.qtr + 1), self.name)
#        self.worksheet.update_acell(str('B') + str(self.qtr + 1), self.qtr)
#        self.worksheet.update_acell(str('C') + str(self.qtr + 1), self.my_revenue(True))
#        self.worksheet.update_acell(str('D') + str(self.qtr + 1), self.my_expenses(True))
#        self.worksheet.update_acell(str('E') + str(self.qtr + 1), self.my_profit(True))
#        self.worksheet.update_acell(str('F') + str(self.qtr + 1),
#                                    'Strategy for next quarter Advert Type:{}, scale: {}'.format(advert_type, scale))

        self.lock.release()

    def record_metric(self):
        
        # calculate the metrics for previous tick and add to tracker: sales, revenue and profit
        # Eg.[{iphone: 1, airpods: 2}]
        self.sales_history.append(self.item_sold)
        revenue = {product: sales * product.price for product, sales in self.item_sold.items()}
        expense = self.expense_history[-1]
        profit = {product: revenue - expense[product] for product, revenue in revenue.items() if product in expense}

        # append revenue and profit record to the history in a list
        # Eg.[{iphone: 1, airpods: 2}, {iphone: 2, airpods: 3}]
        self.revenue_history.append(revenue)
        self.profit_history.append(profit)
        self.sentiment_history.append(self.user_sentiment())
        
        # perform the actions and view the expense
        expense = {key: 0 for key in self.products_list}
        for product in self.products_list:
            expense[product] = GoogleAds.post_advertisement(self, product, advert_type[product], scale[product])
        self.expense_history.append(expense)
        
        return
    
    def my_revenue(self, latest_only=False):
        """
        calculate the total revenue
        :param latest_only: give the revenue in last tick if latest_only = True, else give the total revenue
        :return: total revenue for all products sold (float)
        """
        if latest_only:
            revenue = self.revenue_history[-1]
            total_revenue = sum(revenue.values())
        else:
            total_revenue = sum(sum(revenue.values()) for revenue in self.revenue_history)

        return total_revenue

    def my_expenses(self, latest_only=False):
        """
        calculate the total expense
        :param latest_only: give the expense in last tick if latest_only = True, else give the total expense
        :return: total expense for all products (float)
        """
        if latest_only:
            expense = self.expense_history[-1]
            total_bill = sum(expense.values())
        else:
            total_bill = sum(sum(expense.values()) for expense in self.expense_history)

        return total_bill

    def my_profit(self, latest_only=False):
        """
        calculate the total profit
        :param latest_only: give the profit in last tick if latest_only = True, else give the total profit
        :return: total profit earned from all products sold (float)
        """
        if latest_only:
            profit = self.profit_history[-1]
            total_profit = sum(profit.values())
        else:
            total_profit = sum(sum(profit.values()) for profit in self.profit_history)

        return total_profit
     
    def user_sentiment(self):
        """
        calculates the user sentiment from tweets.
        """
        # initialize sentiment list with 1 for all products representing positive user_sentiment at first
        sentiment_list = {key: 1 for key in self.products_list}
        
        # get the latest tweets and calculate the percentage of positive tweets as user_sentiment
        for product in self.products_list:
            tweets = numpy.asarray(Twitter.get_latest_tweets(product, 100))
            sentiment = 1 if len(tweets) == 0 else (tweets == 'POSITIVE').mean()
            sentiment_list[product] = sentiment

        return sentiment_list

    def my_sales(self, product, latest_only=False):
        """
        calculate sales of product
        :param latest_only: give the sales in last tick if latest_only = True, else give total sales
        :return: total sales for product
        """
        if latest_only:
            total_sales = self.sales_history[-1][product]
        else:
            total_sales = sum(sales[product] for sales in self.sales_history)

        return total_sales
    
    
    def my_inventory(self, product):
        """
        :return: inventory of product in last tick
        """
        return self.inventory[-1][product]


    def kill(self):
        """
        to stop the seller thread
        """
        self.STOP = True
        self.thread.join()

    def __str__(self):
        return self.name

    # Cognition system that decides what to do next.
    def CEO(self):
        """
        Choose advertisement types and scales based on sales, revenue and user_coverage.
        If recent sales is above sales_target or user_coverage is less than target, choose basic ads, otherwise choose targeted ads.
        
        Set total advertisement budget less than a percentage of revenue, to avoid bankrupt
        Scale (number of ads to put) equals to budget divided by advert price.
        
        :return: the type of advert seller want to publish and at what scale for each product
        """
        
        advert_type = {key: GoogleAds.ADVERT_BASIC for key in self.products_list}
        scale = {key: 1 for key in self.products_list}
        
        for product in self.products_list:
            
            sales = self.my_sales(product, True)
            ads_target_sales = 500
            
            revenue = self.revenue_history[-1][product]
            ads_percent = 0.05
            ads_budget = ads_percent * revenue
            
            if GoogleAds.user_coverage(product) < 0.5 or sales > ads_target_sales:
                advert_type[product] = GoogleAds.ADVERT_BASIC
            else:
                advert_type[product] = GoogleAds.ADVERT_TARGETED
            
            # scale = budget/ads price, round down to integer
            scale[product] = max((ads_budget // GoogleAds.advert_price[advert_type]), 1)
        
        return advert_type, scale
    
    def adjust_price(self):
        """
        This function is for seller to increase or reduce price based on historical data:
        1. increase price when average sales is above target.
        2. reduce price when inventory is more than benchmark for a time period
        or average sales volume is lower than benchmark.
        :return: none
        """
        invent_bench = 1000
        sales_target = 100
        sales_bench = 10
        for product in self.products_list:
            
            total_sales = self.my_sales(product)
            qtrs = len(self.sales_history)
            avg_sales = total_sales / qtrs
            price_delta = 0
            
            # 90% price increase for more profit
            if avg_sales > sales_target:
                price_delta = 0.1
            
            # 90% discount promotion to improve sales
            elif avg_sales < sales_bench:
                price_delta = -0.1
            
            # 80% discount to clear inventory
            elif self.my_inventory(product) > invent_bench:
                price_delta = -0.2
            
            product.price = product.price * (1 + price_delta)
        
        return
