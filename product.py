class Product(object):
    def __init__(self, name, price, quality):
        assert quality <= 1

        self.name = name
        self.price = price
        self.quality = quality
