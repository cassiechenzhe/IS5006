import matplotlib.pyplot as plt
import numpy


def plot(seller):
    """
    plot graphs of metrics such as revenue and expense
    :param seller: seller class
    :return: none
    """
    plt.figure(figsize=(6, 9))
    plt.subplots_adjust(hspace=0.5)
    plt.subplot(311)
    plt.plot(seller.my_revenue(), label='Revenue')
    plt.plot(seller.my_expense()[:-1], label='Expenses')
    plt.plot(seller.my_profit(), label='Profit')
    plt.xticks(range(len(seller.my_revenue())))
    plt.legend()
    plt.title(seller.name.upper(), size=16)

    plt.subplot(312)
    plt.plot(numpy.cumsum(seller.my_revenue()), label='Cumulative Revenue')
    plt.plot(numpy.cumsum(seller.my_expense()[:-1]), label='Cumulative Expenses')
    plt.plot(numpy.cumsum(seller.my_profit()), label='Cumulative Profit')
    plt.xticks(range(len(seller.my_revenue())))
    plt.legend()

