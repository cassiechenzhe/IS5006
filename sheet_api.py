import gspread
from oauth2client.service_account import ServiceAccountCredentials

credential_file = 'AutoEmail.json'

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

client = gspread.authorize(ServiceAccountCredentials.from_json_keyfile_name(credential_file, scope))

workbook = client.create("Group_HW3_haha")

#update your email address that has google credentials
workbook.share('a0091882w.receiver@gmail.com', perm_type='user', role='reader')

# Create 2 worksheets for 2 sellers
workbook.add_worksheet('apple', rows=100, cols=100)
workbook.add_worksheet('samsung', rows=100, cols=100)

for sheet in workbook.worksheets():
    sheet.update_acell('A1', 'Seller')
    sheet.update_acell('B1', 'QTR')
    sheet.update_acell('C1', 'Revenue')
    sheet.update_acell('D1', 'Expense')
    sheet.update_acell('E1', 'Profit')
    sheet.update_acell('F1', 'Advertisement Strategy')


