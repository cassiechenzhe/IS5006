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

#lst = [['apple', 1, 'iphone', 20, 30, 10, 20, 'BASIC'], ['apple', 2, 'airpods', 30, 30, 10, 20, 'BASIC'], 
#       ['apple', 3, 'iphone', 40, 30, 10, 20, 'TARGETED'], ['apple', 4, 'phonecase', 20, 30, 10, 20, 'BASIC']]

def update_sheet(sellers_list):
    """
    record sales, revenue, profit in google spreadsheet
    """
    coln_list = ['Seller', 'QTR', 'Product', 'Sales', 'Revenue', 'Expense', 'Profit', 'Advertisement Strategy']
    lst = []
    
    for seller in sellers_list: 
        # update metrics
        sales = seller.sales_history
        revenue = seller.revenue_history
        expense = seller.expense_history
        profit = seller.profit_history
        
        qtr_list = len(sales)
        prd_list = seller.products_list

        for qtr in range(qtr_list):
            for prd in prd_list:
                prd_history = [str(seller.name), int(qtr+1), str(prd.name), int(sales[qtr][prd]), int(revenue[qtr][prd]), int(expense[qtr][prd]), int(profit[qtr][prd]), 'BASIC']
                print(prd_history)
                lst.append(prd_history)
    
    spreadsheet_key = '1H_MLURMBXG1jYapARtWbh_jd6T83huYAb8tSw7kUhv4'
    wks_name = 'Master'
    df = pd.DataFrame(lst, columns = coln_list)
    d2g.upload(df, spreadsheet_key, wks_name, credentials=credentials, row_names=True)
    
    return df



#def update_title(sheet):
#    """
#    update column names in first row
#    """
#    sheet.update_acell('A1', 'Seller')
#    sheet.update_acell('B1', 'QTR')
#    sheet.update_acell('C1', 'Product')
#    sheet.update_acell('D1', 'Sales')
#    sheet.update_acell('E1', 'Revenue')
#    sheet.update_acell('F1', 'Expense')
#    sheet.update_acell('G1', 'Profit')
#    sheet.update_acell('H1', 'Advertisement Strategy')
#    
#    return
#
#def update_sheet(sellers_list):
#    """
#    record sales, revenue, profit in google spreadsheet
#    """
#    for seller in sellers_list:
#        
#        # Create worksheets for seller 
#        workbook.add_worksheet(seller.name, rows=100, cols=100)
#        worksheet = workbook.worksheet(seller.name)
#        
#        # update column title in first row
#        update_title(worksheet)
#        row_num = 1   # move to next row
#        
#        # update metrics
#        sales = seller.sales_history
#        revenue = seller.revenue_history
#        expense = seller.expense_history
#        profit = seller.profit_history
#        
#        qtr_list = len(revenue)
#        prd_list = seller.products_list
#
#        for qtr in range(qtr_list):
#            for prd in prd_list:
#                row_num +=1
#                worksheet.update_acell(str('A') + str(row_num), seller.name)
#                worksheet.update_acell(str('B') + str(row_num), qtr+1)
#                worksheet.update_acell(str('C') + str(row_num), prd.name)
#                worksheet.update_acell(str('D') + str(row_num), sales[qtr][prd])
#                worksheet.update_acell(str('E') + str(row_num), revenue[qtr][prd])
#                worksheet.update_acell(str('F') + str(row_num), expense[qtr][prd])
#                worksheet.update_acell(str('G') + str(row_num), profit[qtr][prd])
#    return
    

#for sheet in workbook.worksheets():
#    sheet.update_acell('A1', 'Seller')
#    sheet.update_acell('B1', 'QTR')
#    sheet.update_acell('C1', 'Revenue')
#    sheet.update_acell('D1', 'Expense')
#    sheet.update_acell('E1', 'Profit')
#    sheet.update_acell('F1', 'Advertisement Strategy')

        # google sheet to store records
        #self.worksheet = sheet_api.workbook.worksheet(self.name)

# write into google worksheet

#        self.worksheet.update_acell(str('A') + str(self.qtr + 1), self.name)
#        self.worksheet.update_acell(str('B') + str(self.qtr + 1), self.qtr)
#        self.worksheet.update_acell(str('C') + str(self.qtr + 1), self.my_revenue(True))
#        self.worksheet.update_acell(str('D') + str(self.qtr + 1), self.my_expenses(True))
#        self.worksheet.update_acell(str('E') + str(self.qtr + 1), self.my_profit(True))
#        self.worksheet.update_acell(str('F') + str(self.qtr + 1),
#                                    'Strategy for next quarter Advert Type:{}, scale: {}'.format(advert_type, scale))
