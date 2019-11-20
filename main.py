import random
import time

from constants import seed
from customer import Customer
from product import Product
from seller import Seller
from utils import plot

random.seed(seed)

# Create some Consumers
customers = [Customer(name='consumer_' + str(i), wallet=500, tolerance=0.5 + 0.4 * random.random()) for i in range(500)]

# Create products
iphone = Product(name='iphone', price=300, quality=0.9)
airpods = Product(name='airpods', price=50, quality=0.9)
phonecase = Product(name='phonecase', price=5, quality=0.6)
galaxy = Product(name='galaxy', price=200, quality=0.8)
redmi = Product(name='redmi', price=200, quality=0.8)
mate = Product(name='mate', price=200, quality=0.8)

# Create Sellers with some budget
# Each seller can sell multiple products
seller_apple = Seller(name='apple', products_list=[iphone,airpods,phonecase], wallet=1000)
seller_samsung = Seller(name='samsung', products_list=[galaxy, phonecase], wallet=500)
seller_xiaomi = Seller(name='xiaomi', products_list=[redmi, phonecase], wallet=500)
seller_huawei = Seller(name='huawei', products_list=[mate, phonecase], wallet=500)

# Wait till the simulation ends
try:
    time.sleep(20)
except KeyboardInterrupt:
    pass

# kill seller thread
seller_apple.kill()
seller_samsung.kill()

# Plot the sales and expenditure trends
plot(seller_apple)
plot(seller_samsung)

print('Total Profit Apple:', seller_apple.my_profit())
print('Total Profit Samsung:', seller_samsung.my_profit())

# Kill consumer threads
for consumer in customers:
    consumer.kill()
