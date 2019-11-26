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
#        self.advert_type = {key: GoogleAds.ADVERT_BASIC for key in self.products_list}
#        self.promo_effec = {key: 1 for key in self.products_list}
        
#        self.expense = {key: 1 for key in self.products_list}

        # inventory is a list of dictionary with product as key and inventory number as value for each quarter
        # assume initial inventory is 1000 items for each product. Eg.{iphone: 1000, airpods: 1000}
        self.inventory = {key: 500 for key in products_list}

        # sales, revenue, profit, expense and sentiment history start with zero for each product
        # Eg.[{iphone: 0, airpods: 0}] {key: 0 for key in products_list}
        self.sales_history = []
        self.revenue_history = []
        self.profit_history = []
        self.expense_history = [{key: 0 for key in products_list}]
        self.sentiment_history = []     
        self.advert_history = [{key: (GoogleAds.ADVERT_BASIC, 1) for key in products_list}]
        self.promo_history = []
        self.buyer_history = []
        self.total_revenue = []
        self.total_expense = []
        self.total_profit = []
        self.budget = [wallet]

        # qtr number
#        self.qtr = 0

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
        :return: available or not
        """
        self.lock.acquire()
        self.item_sold[product] += 1    
        self.lock.release()            
#        self.inventory[product] -= self.item_sold[product]
        
        return 'YES'
            
    
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
        
        self.item_sold = self.item_sold.fromkeys(self.item_sold, 0)

        self.lock.release()
        
        self.record_metric()
#        print('\n\nSeller: ', self.name)
#        print('Sales in previous quarter:', self.my_sales(True))
#        print('Revenue in previous quarter:', self.my_revenue(True))
#        print('Expenses in previous quarter:', self.my_expenses(True))
#        print('Profit in previous quarter:', self.my_profit(True))

        # add the profit to seller's wallet
        self.wallet += self.new_profit()
        self.budget.append(self.wallet)

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
        revenue = {k: v * (k.price) for k, v in self.sales_history[-1].items()}
        expense = self.expense_history[-1]
        profit = {k: v - expense[k] for k, v in revenue.items() if k in expense}
        ads_scale = self.advert_history[-1]
        promo_effect = {k: float(v/ads_scale[k][1]) for k, v in self.sales_history[-1].items() if k in ads_scale}    
        
        num_buyer = {k: len(set(GoogleAds.purchase_history[k])) for k in self.products_list}
        
        # append revenue and profit record to the history in a list
        # Eg.[{iphone: 1, airpods: 2}, {iphone: 2, airpods: 3}]
        self.revenue_history.append(revenue)
        self.profit_history.append(profit)
        self.sentiment_history.append(self.user_sentiment())
        self.promo_history.append(promo_effect)
        self.buyer_history.append(num_buyer)
        
#        self.total_revenue.append(sum(revenue.values()))
#        self.total_expense.append(sum(expense.values()))
#        self.total_profit.append(sum(profit.values()))
        
        #self.expense.fromkeys(self.expense, 0)
        #self.advert_type.fromkeys(self.advert_type, GoogleAds.ADVERT_BASIC)
        #self.promo_effec.fromkeys(self.promo_effec, 1)
        
        return
    
    def my_revenue(self):
        """
        sum total revenue for all products in each time tick
        :return: list of revenue
        """           
        return [sum(revenue.values()) for revenue in self.revenue_history]

    def my_expense(self):
        """
        sum total expense for all products in each time tick
        :return: list of expense
        """           
        return [sum(expense.values()) for expense in self.expense_history]
    
    def my_profit(self):
        """
        sum total profit for all products in each time tick
        :return: list of profit
        """           
        return [sum(profit.values()) for profit in self.profit_history]

    def new_profit(self):
        """
        calculate the latest total profit
        :return: total profit earned from all products sold (float)
        """
        return sum(self.profit_history[-1].values())

  
#    def my_revenue(self, latest_only=False):
#        """
#        calculate the total revenue
#        :param latest_only: give the revenue in last tick if latest_only = True, else give the total revenue
#        :return: total revenue for all products sold (float)
#        """
#        if latest_only:
#            revenue = self.revenue_history[-1]
#            sum_revenue = sum(revenue.values())
#        else:
#            sum_revenue = sum(sum(revenue.values()) for revenue in self.revenue_history)
#
#        return sum_revenue
#
#    def my_expenses(self, latest_only=False):
#        """
#        calculate the total expense
#        :param latest_only: give the expense in last tick if latest_only = True, else give the total expense
#        :return: total expense for all products (float)
#        """
#        if latest_only:
#            expense = self.expense_history[-1]
#            total_bill = sum(expense.values())
#        else:
#            total_bill = sum(sum(expense.values()) for expense in self.expense_history)
#
#        return total_bill
#
#    def my_profit(self, latest_only=False):
#        """
#        calculate the total profit
#        :param latest_only: give the profit in last tick if latest_only = True, else give the total profit
#        :return: total profit earned from all products sold (float)
#        """
#        if latest_only:
#            profit = self.profit_history[-1]
#            total_profit = sum(profit.values())
#        else:
#            total_profit = sum(sum(profit.values()) for profit in self.profit_history)
#
#        return total_profit
    
#    def my_sales(self, latest_only=False):
#        """
#        calculate total sales
#        :param latest_only: give the sales in last tick if latest_only = True, else give total sales
#        :return: total sales for all products
#        """
#        if latest_only:
#            sales = self.sales_history[-1]
#            total_sales = sum(sales.values())
#        else:
#            total_sales = sum(sum(sales.values()) for sales in self.sales_history)
#
#        return total_sales     
    
    def user_sentiment(self):
        """
        calculates the user sentiment from tweets.
        :return: a dictionary of sentiment value for each product as key
        """
        # initialize sentiment list with 1 for all products representing positive user_sentiment at first
#        sentiment_list = {key: 1 for key in self.products_list}
        sentiment_list = {}
        # get the latest tweets and calculate the percentage of positive tweets as user_sentiment
        for product in self.products_list:
            tweets = np.asarray(Twitter.get_latest_tweets(product, 10))
            sentiment = 1 if len(tweets) == 0 else (tweets == 'POSITIVE').mean()
            sentiment_list.update({product: sentiment})

        return sentiment_list

#    def prd_sales(self, product, latest_only=False):
#        """
#        calculate sales of product
#        :param latest_only: give the sales in last tick if latest_only = True, else give total sales
#        :return: total sales for product
#        """
#        if latest_only:
#            prd_sales = self.sales_history[-1][product]
#        else:
#            prd_sales = sum(sales[product] for sales in self.sales_history)
#        return prd_sales

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
        advert_type = {}
        expense = {}
        ads_type = GoogleAds.ADVERT_BASIC
             
        ads_percent = 0.5
        max_budget = self.wallet * 0.2
        
        #avoid bankrupt
        for product in self.products_list:
            revenue = self.revenue_history[-1][product]
            ads_budget = max(ads_percent * revenue, max_budget)
            coverage = GoogleAds.user_coverage(product)
            
            if coverage > 0.5:
                ads_type = GoogleAds.ADVERT_TARGETED

            scale = min(int(ads_budget / GoogleAds.advert_price[ads_type]), 500)
                        
        # perform the actions and view the expense
            advert_type.update({product: (ads_type, scale)})
        
            expense.update({product: GoogleAds.post_advertisement(self, product, ads_type, scale)})
        
        # store expense data
        self.advert_history.append(advert_type)
        self.expense_history.append(expense)
               
        return
    
    def adjust_price(self):
        """
        This function is for seller to increase or reduce price based on historical data:
        1. increase price when average sales is above target.
        2. reduce price when inventory is more than benchmark for a time period
        or average sales volume is lower than benchmark.
        :return: none
        """
        invent_bench = 800
        invent_min = 100
        sales_target = 200
        sales_bench = 2
        for product in self.products_list:
            
            total_sales = self.sales_history[-1][product]
            qtrs = len(self.sales_history)
            avg_sales = total_sales / qtrs
            price_delta = 0
            
            # adjust price 2 qtrs after market start
            if qtrs > 2:
                # 30% price increase for more profit
                if avg_sales > sales_target or self.inventory[product] < invent_min:
                    price_delta = 0.3
                
                # 90% discount promotion to improve sales
                elif avg_sales < sales_bench:
                    price_delta = -0.1
                
                # 80% discount to clear inventory
                elif self.inventory[product] > invent_bench:
                    price_delta = -0.2
            
            product.price = int(product.price * (1 + price_delta))
        
        return
