import random
import time
import pandas as pd

from constants import seed
from customer import Customer
from product import Product
from seller import Seller
from utils import plot
import sheet_api

from twitter import Twitter

print("Please remember install df2gspread library to interact with Google Spreadsheets if you haven't.")
random.seed(seed)

# Create products
iphone = Product(name='iphone', price=600, quality=0.9)
airpods = Product(name='airpods', price=100, quality=0.6)
phonecase = Product(name='phonecase', price=30, quality=0.6)
galaxy = Product(name='galaxy', price=500, quality=0.7)
tv = Product(name='tv', price=1000, quality=0.7)
redmi = Product(name='redmi', price=200, quality=0.6)
robotvac = Product(name='robot_vacuum', price=1000, quality=0.7)
mate = Product(name='mate', price=300, quality=0.8)
laptop = Product(name='laptop', price=600, quality=0.6)

prd_list = [iphone, airpods, phonecase, galaxy, tv, redmi, robotvac, mate, laptop]

# Create some Consumers
sensitive_customers = [Customer(name='consumer_' + str(i), wallet=3000, products_list=prd_list,tolerance=0.7 + 0.2 * random.random()) for i in range(300)]
insensitive_customers = [Customer(name='consumer_' + str(i), wallet=3000, products_list=prd_list,tolerance=0.5 + 0.4 * random.random()) for i in range(300, 500)]

# Create Sellers with some budget
# Each seller can sell multiple products
seller_apple = Seller(name='apple', products_list=[iphone,airpods,phonecase], wallet=1000)
seller_samsung = Seller(name='samsung', products_list=[galaxy,tv], wallet=800)
seller_xiaomi = Seller(name='xiaomi', products_list=[redmi, robotvac], wallet=500)
seller_huawei = Seller(name='huawei', products_list=[mate, laptop], wallet=600)

# Wait till the simulation ends
print('\nHello! Welcome to the Market. Transaction in progress. Lets wait...')
try:
    time.sleep(10)
except KeyboardInterrupt:
    pass

# kill seller thread
seller_apple.kill()
seller_samsung.kill()
seller_xiaomi.kill()
seller_huawei.kill()

# Plot the sales and expenditure trends
plot(seller_apple)
plot(seller_samsung)
plot(seller_xiaomi)
plot(seller_huawei)

print('\nResult:\n')
print('Total Profit Apple:', int(sum(seller_apple.my_profit())))
print('Total Profit Samsung:', int(sum(seller_samsung.my_profit())))
print('Total Profit Xiaomi:', int(sum(seller_xiaomi.my_profit())))
print('Total Profit Huawei:', int(sum(seller_huawei.my_profit())))
print('\nPlotting graphs:\n')

#print('Twitter: ', Twitter.get_latest_tweets(laptop, 5))
# Use fuzzy logic to choose the seller which is most profitable and somewhat high sales
def fuzzy_logic():
    return

sellers_list = [seller_apple, seller_samsung, seller_xiaomi, seller_huawei]
#sheet_api.update_sheet(sellers_list)

# Kill consumer threads
for consumer in sensitive_customers:
    consumer.kill()
for consumer in insensitive_customers:
    consumer.kill()
