import random
import time

from constants import seed
from customer import Customer
from product import Product
from seller import Seller
from utils import plot

random.seed(seed)

# Create some Consumers
customers = [Customer(name='consumer_' + str(i), wallet=3000, tolerance=0.5 + 0.4 * random.random()) for i in range(500)]

# Create products
iphone = Product(name='iphone', price=500, quality=0.9)
airpods = Product(name='airpods', price=50, quality=0.9)
phonecase = Product(name='phonecase', price=30, quality=0.6)
galaxy = Product(name='galaxy', price=450, quality=0.8)
redmi = Product(name='redmi', price=200, quality=0.7)
mate = Product(name='mate', price=450, quality=0.9)

# Create Sellers with some budget
# Each seller can sell multiple products
seller_apple = Seller(name='apple', products_list=[iphone,airpods,phonecase], wallet=10000)
seller_samsung = Seller(name='samsung', products_list=[galaxy, phonecase], wallet=8000)
seller_xiaomi = Seller(name='xiaomi', products_list=[redmi, phonecase], wallet=5000)
seller_huawei = Seller(name='huawei', products_list=[mate, phonecase], wallet=6000)

# Wait till the simulation ends
try:
    time.sleep(2)
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

# Kill consumer threads
for consumer in customers:
    consumer.kill()
