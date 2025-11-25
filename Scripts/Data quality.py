import pandas as pd

products = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/interim/products_cl.csv')
orders = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/interim/orders_cl.csv',
                     parse_dates=['created_date'])
orderlines = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/interim/orderlines_cl.csv',
                         parse_dates=['date'])
brands = pd.read_csv('C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/interim/brands_cl.csv')

#makesure that dates 

### Check the consistency of keys between tables==============================================================================================

#Set intersection of orders and orderlines
common_ids = set(orders.order_id) & set(orderlines.order_id)
orders_qu = orders[orders.order_id.isin(common_ids)]
orderlines_qu = orderlines[orderlines.order_id.isin(common_ids)]

#Set intersection of products and orderlines
common_ids = set(orderlines_qu.sku) & set(products.sku)

#Find the orders with a missing product by finding the rows in the orderline table and then the set of orders associated with this
affected_orders = set(orderlines[~orderlines.sku.isin(common_ids)].order_id)

#remove these orders from the orders and orderlines tables
orders_qu = orders_qu[~orders_qu.order_id.isin(affected_orders)]
orderlines_qu = orderlines_qu[~orderlines_qu.order_id.isin(affected_orders)]


### Check numerical consistency between tables==============================================================================================

#Add new column for revenue: quantity * price
orderlines_qu['revenue'] = orderlines_qu.unit_price * orderlines_qu.product_quantity
#Group orderlines by order_id to find total paid per order
orderlines_grped = orderlines_qu.groupby('order_id', as_index=False)['revenue'].sum()
#merge this back into the orders table to compare against total_paid from this column
compare_df = orders_qu.merge(orderlines_grped, on='order_id')
#calculate the difference between the two measures
compare_df['diff'] = compare_df.total_paid - compare_df.revenue

#Flag any differences outside of a certain tolerance
compare_df['suspicious'] = ~(compare_df['diff'].between(-1, 20))
#Find all order ids with suspicious orders
suspicious_ids = set(compare_df[compare_df.suspicious].order_id)

#produce final tables
orders_final = orders_qu[~orders_qu.order_id.isin(suspicious_ids)]
orderlines_final = orderlines_qu[~orderlines_qu.order_id.isin(suspicious_ids)]


### Write final tables to processed data folder for use ========================================================================================
path = 'C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/orderlines.csv'
orderlines_final.to_csv(path,index=False)
path = 'C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/orders.csv'
orders_final.to_csv(path,index=False)


#Add products and brands to processed folder despite no changes
path = 'C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/products.csv'
products.to_csv(path,index=False)
path = 'C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/brands.csv'
brands.to_csv(path,index=False)

#Create a fully merged table
#merge orders and orderlines
merge1 = orderlines_final.merge(orders_final, on='order_id')

#add brand name to products
products['short'] = products.sku.str.slice(stop=3)
products = products.merge(brands, on='short')

#merge products to orders and lines
full_df = merge1.merge(products, on='sku')

#Write this full merged dataframe to the data folder
path = 'C:/Users/admin/Documents/1WBS/3Data_Cln_Stry/eniac_cleaning/data/processed/full_df.csv'
full_df.to_csv(path,index=False)
