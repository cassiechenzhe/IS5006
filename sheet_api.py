import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import df2gspread as d2g

credential_file = 'MAS.json'

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scope)

client = gspread.authorize(credentials)

#workbook = client.create("IS5006_Project")
#workbook = client.open("IS5006_Project")

#update your email address that has google credentials
#workbook.share('a0091882w.receiver@gmail.com', perm_type='user', role='owner')


def update_sheet(sellers_list):
    """
    record sales, revenue, profit in google spreadsheet
    return: data frame of history record
    """
    coln_list = ['Seller', 'QTR', 'Product', 'Sales', 'Revenue', 'Expense',
                 'Profit', 'Advertisement Strategy', 'Promotion Effectiveness',
                 'Num of Buyers', 'Budget']
    lst = []
    
    for seller in sellers_list: 
        # update metrics
        sales = seller.sales_history
        revenue = seller.revenue_history
        expense = seller.expense_history
        profit = seller.profit_history
        advert = seller.advert_history
        promo = seller.promo_history
        buyer = seller.buyer_history
        budget = seller.budget 
        
        qtr_list = len(sales)
        prd_list = seller.products_list

        for qtr in range(qtr_list):
            for prd in prd_list:
                prd_history = [str(seller.name), int(qtr+1), str(prd.name),
                               int(sales[qtr][prd]), int(revenue[qtr][prd]),
                               int(expense[qtr][prd]), int(profit[qtr][prd]),
                               str(advert[qtr][prd]), round(promo[qtr][prd],2), int(buyer[qtr][prd]), int(budget[qtr])]
                
                lst.append(prd_history)
    
    # spread sheet address
    spreadsheet_key = '1H_MLURMBXG1jYapARtWbh_jd6T83huYAb8tSw7kUhv4'
    # workbook name
    wks_name = 'Master'
    df = pd.DataFrame(lst, columns = coln_list)
    # write data frame to spread sheet
    d2g.upload(df, spreadsheet_key, wks_name, credentials=credentials, row_names=True)
    
    return df
