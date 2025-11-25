# -*- coding: utf-8 -*-
"""
A python script for cleaning our data
"""
import pandas as pd


#read in the raw data
orders_raw = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/raw/orders.csv')
orderlines_raw = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/raw/orderlines.csv')
brands_raw = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/raw/brands.csv')
products_raw = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/raw/products.csv')

#Function that can remove the first decimal from a number (formatted as a string), when there are two
def clean_double_decimal (df: pd.DataFrame, cols: list):
    for col in cols:
        mask = df[col].str.count('\.') > 1
        df.loc[mask, col] = df.loc[mask, col].str.replace('\.', '', n=1, regex=True)
    return (df)

#Cleaning brands table===========================================================================
brands = brands_raw.copy().convert_dtypes()
#Save to csv
path='C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/interim/brands_cl.csv'
brands.to_csv(path, index=False)


#Cleaning orders table===========================================================================

#Drop NA values from the orders table
orders = orders_raw.copy().dropna(axis=0).convert_dtypes()

#Change date in orders table to datetime
orders.created_date = pd.to_datetime(orders.created_date)

#Save to csv
path='C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/interim/orders_cl.csv'
orders.to_csv(path, index=False)


#Cleaning orderlines table===========================================================================

#Make date a date type
orderlines = orderlines_raw.copy().convert_dtypes()
orderlines["date"] = pd.to_datetime(orderlines["date"])
#Remove double decimals from orderlines unit price
orderlines = clean_double_decimal(orderlines, ['unit_price'])
#Convert unit price to numeric
orderlines["unit_price"] = pd.to_numeric(orderlines["unit_price"])
#Remove the useless product_id column
orderlines.drop('product_id', axis=1, inplace=True)
#Rename order_id for better merging
orderlines.rename({'id_order' : 'order_id'}, inplace=True, axis=1)
#Save the cleaned data to a csv file
path = 'C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/interim/orderlines_cl.csv'
orderlines.to_csv(path,index=False)


#Cleaning products table===========================================================================

#Drop duplicates from the products table and autoupdate data types
products = products_raw.copy().drop_duplicates().convert_dtypes()

#Drop missing values from the price column  (but not missing descriptions or types)
products.dropna(subset='price', inplace=True)

#drop promo price
products.drop('promo_price', axis=1, inplace=True)

#Run custom function
products = clean_double_decimal(products, ['price'])

#Remove questionable lines with three decimals after the point
products = products[~(products.price.astype(str).str.contains(r'\.\d{3}$'))]


#Change the price to numeric
products[['price']] = products[['price']].astype(float)

### Add number of times each product has been sold from the orderlines table to product table
prod_times_sold = orderlines.groupby('sku', as_index=False).agg(times_sold=('sku', 'size'))
products = products.merge(prod_times_sold, on='sku', how='left')

path = 'C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/interim/products_cl.csv'
products.to_csv(path,index=False)

