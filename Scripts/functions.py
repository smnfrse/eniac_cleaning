import pandas as pd

def open_data():
    products = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/products.csv')
    orders = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/orders.csv',
                        parse_dates=['created_date'])
    orderlines = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/orderlines.csv',
                            parse_dates=['date'])
    brands = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/brands.csv')
    full_df = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/full_df.csv',
                        parse_dates=['date', 'created_date'])
    return products, orders, orderlines, brands, full_df