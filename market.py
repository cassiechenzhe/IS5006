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
    def buy(buyer, product_list):
        # give discount for more than 2 products      
        if len(product_list) >= 2:
            discount_factor = 0.9
        else:
            discount_factor = 1   
        
        for product in product_list:
            # get the seller for product from catalogue
            seller = Market.catalogue[product]
            
            # call seller's sold function which returns True if product is available; otherwise transaction fails
            if seller.sold(product):    
                # deduct price from user's balance
                buyer.deduct(product.price*discount_factor)
                # track user
                GoogleAds.track_user_purchase(buyer, product)
            else:
                return False

        return True
    
#    # return all products registered in the market
    @staticmethod
    def get_products():
        return list(Market.catalogue.keys())
