import matplotlib.pyplot as plt
import numpy


def plot(seller):
    plt.figure(figsize=(6, 9))
    plt.subplots_adjust(hspace=0.5)
    plt.subplot(311)
    plt.plot(seller.revenue_history, label='Revenue')
    plt.plot(seller.expense_history[:-1], label='Expenses')
    plt.plot(seller.profit_history, label='Profit')
    plt.xticks(range(len(seller.revenue_history)))
    plt.legend()
    plt.title(seller.name.upper(), size=16)

    plt.subplot(312)
    plt.plot(numpy.cumsum(seller.revenue_history), label='Cumulative Revenue')
    plt.plot(numpy.cumsum(seller.expense_history[:-1]), label='Cumulative Expenses')
    plt.plot(numpy.cumsum(seller.profit_history), label='Cumulative Profit')
    plt.xticks(range(len(seller.revenue_history)))
    plt.legend()

    plt.subplot(313)
    plt.plot(seller.sentiment_history, label='User Sentiment')
    plt.xticks(range(len(seller.revenue_history)))
    plt.legend()
    plt.show()
