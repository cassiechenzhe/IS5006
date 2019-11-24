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
iphone = Product(name='iphone', price=600, quality=0.9)
airpods = Product(name='airpods', price=50, quality=0.6)
phonecase = Product(name='phonecase', price=30, quality=0.5)
galaxy = Product(name='galaxy', price=450, quality=0.7)
tv = Product(name='tv', price=1000, quality=0.4)
redmi = Product(name='redmi', price=200, quality=0.5)
robotvac = Product(name='robot_vacuum', price=1000, quality=0.7)
mate = Product(name='mate', price=300, quality=0.6)
laptop = Product(name='laptop', price=400, quality=0.8)

prd_list = [iphone, airpods, phonecase, galaxy, tv, redmi, robotvac, mate, laptop]
relation = pd.DataFrame(data=0.5,index=prd_list, columns=prd_list)
relation.loc[iphone][airpods] = 0.8
relation.loc[iphone][phonecase] = 0.9
relation.loc[airpods][phonecase] = 0.9

# Create some Consumers
sensitive_customers = [Customer(name='consumer_' + str(i), wallet=3000, products_list=prd_list,tolerance=0.7 + 0.2 * random.random()) for i in range(300)]
insensitive_customers = [Customer(name='consumer_' + str(i), wallet=2000, products_list=prd_list,tolerance=0.3 + 0.6 * random.random()) for i in range(300, 500)]

# Create Sellers with some budget
# Each seller can sell multiple products
seller_apple = Seller(name='apple', products_list=[iphone,airpods,phonecase], wallet=1000)
seller_samsung = Seller(name='samsung', products_list=[galaxy,tv], wallet=800)
seller_xiaomi = Seller(name='xiaomi', products_list=[redmi, robotvac], wallet=500)
seller_huawei = Seller(name='huawei', products_list=[mate, laptop], wallet=600)

# Wait till the simulation ends
try:
    time.sleep(5)
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

print('Total Profit Apple:', int(seller_apple.my_profit()))
print('Total Profit Samsung:', int(seller_samsung.my_profit()))
print('Total Profit Xiaomi:', int(seller_xiaomi.my_profit()))
print('Total Profit Huawei:', int(seller_huawei.my_profit()))

#sellers_list = [seller_apple, seller_samsung, seller_xiaomi, seller_huawei]
#sheet_api.update_sheet(sellers_list)

# Kill consumer threads
for consumer in sensitive_customers:
    consumer.kill()
for consumer in insensitive_customers:
    consumer.kill()
