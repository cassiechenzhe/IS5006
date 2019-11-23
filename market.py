from threading import Lock

from google_ads import GoogleAds


class Market(object):
    catalogue = {}
    lock = Lock()

    # initialise the seller catalogue
    @staticmethod
    def register_seller(seller, product):
        Market.lock.acquire()
        Market.catalogue[product] = seller
        Market.lock.release()

    # when a user buys a product, increment the seller's sales
    @staticmethod
    def buy(buyer, product):
        # get the seller for product from catalogue
        seller = Market.catalogue[product]

        # call seller's sold function
        seller.sold(product)
        
        # print to debug
        # print('\nSeller: ', seller.name, ' Product: ', product.name)

        # deduct price from user's balance
        buyer.deduct(product.price)

        # track user
        GoogleAds.track_user_purchase(buyer, product)
    
#    # return all products registered in the market
    @staticmethod
    def get_products():
        return list(Market.catalogue.keys())
