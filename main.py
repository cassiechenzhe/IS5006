import random
import time
import pandas as pd

from constants import seed
from customer import Customer
from product import Product
from seller import Seller
from utils import plot
import sheet_api

random.seed(seed)

# Create products
iphone = Product(name='iphone', price=500, quality=0.9)
airpods = Product(name='airpods', price=50, quality=0.9)
phonecase = Product(name='phonecase', price=30, quality=0.6)
galaxy = Product(name='galaxy', price=450, quality=0.8)
tv = Product(name='tv', price=1000, quality=0.9)
redmi = Product(name='redmi', price=200, quality=0.7)
robotvac = Product(name='robot_vacuum', price=1000, quality=0.9)
mate = Product(name='mate', price=450, quality=0.9)
laptop = Product(name='laptop', price=450, quality=0.9)

prd_list = [iphone, airpods, phonecase, galaxy, tv, redmi, robotvac, mate, laptop]
relation = pd.DataFrame(data=0.5,index=prd_list, columns=prd_list)
relation.loc[iphone][airpods] = 0.8
relation.loc[iphone][phonecase] = 0.9
relation.loc[airpods][phonecase] = 0.9

# Create some Consumers
customers = [Customer(name='consumer_' + str(i), wallet=3000, products_list=prd_list,tolerance=0.5 + 0.4 * random.random()) for i in range(500)]

# Create Sellers with some budget
# Each seller can sell multiple products
seller_apple = Seller(name='apple', products_list=[iphone,airpods,phonecase], wallet=10000)
seller_samsung = Seller(name='samsung', products_list=[galaxy,tv], wallet=8000)
seller_xiaomi = Seller(name='xiaomi', products_list=[redmi, robotvac], wallet=5000)
seller_huawei = Seller(name='huawei', products_list=[mate, laptop], wallet=6000)

# Wait till the simulation ends
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
#plot(seller_apple)
#plot(seller_samsung)
#plot(seller_xiaomi)
#plot(seller_huawei)

print('Total Profit Apple:', seller_apple.my_profit())
print('Total Profit Samsung:', seller_samsung.my_profit())
print('Total Profit Xiaomi:', seller_xiaomi.my_profit())
print('Total Profit Huawei:', seller_huawei.my_profit())

#sellers_list = [seller_apple, seller_samsung, seller_xiaomi, seller_huawei]
#sheet_api.update_sheet(sellers_list)

# Kill consumer threads
for consumer in customers:
    consumer.kill()
