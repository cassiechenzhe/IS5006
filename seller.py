import time
from threading import Lock, Thread

import numpy as np
import pandas as pd

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
        self.products_list = products_list
        # self.product = product
        self.wallet = wallet

        # register the seller with each product it owns in market
        if products_list is not None:
            for product in products_list:
                Market.register_seller(self, product)
        
        # establish relationships between products
        # relate_factor = pd.DataFrame(index=products_list, columns=products_list)
        
        
        # metrics tracker:
        # item_sold is total number of items of each product sold by seller.
        # A dictionary with each product as key and value is no. of items sold.eg.{iphone: 0, airpods: 0}
        self.item_sold = {key: 0 for key in products_list}
        
        # advert_type and scale store data of advertisement strategy and users viewing ads for each product
        # expense is expense of advertisement
        self.advert_type = {key: GoogleAds.ADVERT_BASIC for key in self.products_list}
        self.promo_effec = {key: 1 for key in self.products_list}
        
        self.expense = {key: 1 for key in self.products_list}

        # inventory is a list of dictionary with product as key and inventory number as value for each quarter
        # assume initial inventory is 1000 items for each product. Eg.[{iphone: 1000, airpods: 1000}]
        self.inventory_history = [{key: 1000 for key in products_list}]

        # sales, revenue, profit, expense and sentiment history start with zero for each product
        # Eg.[{iphone: 0, airpods: 0}]
        self.sales_history = [{key: 0 for key in products_list}]
        self.revenue_history = [{key: 0 for key in products_list}]
        self.profit_history = [{key: 0 for key in products_list}]
        self.expense_history = [{key: 0 for key in products_list}]
        self.sentiment_history = [{key: 1 for key in products_list}]
        self.advert_history = []
        self.promo_history = []

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
        #self.qtr += 1
        
        self.sales_history.append(self.item_sold)

        self.lock.release()
         
        print('\n\nSeller: ', self.name)
        print('Sales in previous quarter:', self.my_sales(True))
        print('Revenue in previous quarter:', self.my_revenue(True))
        print('Expenses in previous quarter:', self.my_expenses(True))
        print('Profit in previous quarter:', self.my_profit(True))
               
        self.record_metric()

        # add the profit to seller's wallet
        self.wallet += self.my_profit(True)

        # reset the sales counter
        #self.item_sold.fromkeys(self.item_sold, 0)
        
        # adjust price for next time step
        self.adjust_price()

        # choose advertisement strategy for next time step
        self.CEO()
        
        #print('\nStrategy for next quarter \nProduct: {}, Advert Type: {}, scale: {}\n\n'.format(product.name, advert_type[product], scale[product]) for product in self.products_list)
        return

    def record_metric(self):
        
        # calculate the metrics for previous tick and add to tracker: sales, revenue and profit
        # Eg.[{iphone: 1, airpods: 2}]
        #self.sales_history.append(self.item_sold)
        revenue = {product: sales * product.price for product, sales in self.item_sold.items()}
        expense = self.expense_history[-1]
        profit = {product: revenue - expense[product] for product, revenue in revenue.items() if product in expense}
        
        # append revenue and profit record to the history in a list
        # Eg.[{iphone: 1, airpods: 2}, {iphone: 2, airpods: 3}]
        self.revenue_history.append(revenue)
        self.profit_history.append(profit)
        self.sentiment_history.append(self.user_sentiment())        
        self.advert_history.append(self.advert_type)
        self.promo_history.append(self.promo_effec)
        
        self.item_sold.fromkeys(self.item_sold, 0)
        self.expense.fromkeys(self.expense, 0)
        self.advert_type.fromkeys(self.advert_type, GoogleAds.ADVERT_BASIC)
        self.promo_effec.fromkeys(self.promo_effec, 1)
        
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
    
    def my_sales(self, latest_only=False):
        """
        calculate total sales
        :param latest_only: give the sales in last tick if latest_only = True, else give total sales
        :return: total sales for all products
        """
        if latest_only:
            sales = self.sales_history[-1]
            total_sales = sum(sales.values())
        else:
            total_sales = sum(sum(sales.values()) for sales in self.sales_history)

        return total_sales     
    
    def user_sentiment(self):
        """
        calculates the user sentiment from tweets.
        """
        # initialize sentiment list with 1 for all products representing positive user_sentiment at first
        sentiment_list = {key: 1 for key in self.products_list}
        
        # get the latest tweets and calculate the percentage of positive tweets as user_sentiment
        for product in self.products_list:
            tweets = np.asarray(Twitter.get_latest_tweets(product, 100))
            sentiment = 1 if len(tweets) == 0 else (tweets == 'POSITIVE').mean()
            sentiment_list[product] = sentiment

        return sentiment_list

    def prd_sales(self, product, latest_only=False):
        """
        calculate sales of product
        :param latest_only: give the sales in last tick if latest_only = True, else give total sales
        :return: total sales for product
        """
        if latest_only:
            prd_sales = self.sales_history[-1][product]
        else:
            prd_sales = sum(sales[product] for sales in self.sales_history)
        return prd_sales

    def prd_inventory(self, product, latest_only=False):
        """
        :return: inventory of product in last tick
        """
        if latest_only:
            prd_inventory = self.inventory_history[-1][product]
        else:
            prd_inventory = sum(inv[product] for inv in self.inventory_history)        
        return prd_inventory


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
        
        :return: none
        """
        for product in self.products_list:
            sales = self.prd_sales(product, True)
            ads_target_sales = 10
             
            revenue = self.revenue_history[-1][product]
            ads_percent = 0.1
            if revenue == 0:
                ads_budget = 0.5 * self.wallet #avoid bankrupt
            else:
                ads_budget = ads_percent * revenue
            
            ads_type = GoogleAds.ADVERT_BASIC
            
            promo_effet = GoogleAds.user_coverage(product)
            
            if promo_effet > 0.5 and sales < ads_target_sales:
                ads_type = GoogleAds.ADVERT_TARGETED
 
            # scale = budget/ads price, round down to integer
            # scale = max((ads_budget // GoogleAds.advert_price[ads_type]), 1)
            scale = max(int(ads_budget / GoogleAds.advert_price[ads_type]), 1)
                        
            # perform the actions and view the expense
            self.advert_type[product] = ads_type
            #self.scale[product] = scale
            self.promo_effec[product] = min(0, float(sales/scale))
            self.expense[product] = GoogleAds.post_advertisement(self, product, ads_type, scale)
        
        # store expense data
        self.expense_history.append(self.expense)
        
        return
    
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
            
            total_sales = self.prd_sales(product)
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
            elif self.prd_inventory(product) > invent_bench:
                price_delta = -0.2
            
            product.price = product.price * (1 + price_delta)
        
        return
