"""Perform data quality checks and create final processed datasets."""
from pathlib import Path

import pandas as pd
import numpy as np
from loguru import logger
import typer

from Smn.config import INTERIM_DATA_DIR, PROCESSED_DATA_DIR

app = typer.Typer()


@app.command()
def main(
    # Input files - using CCDS path structure (from interim data)
    products_input: Path = INTERIM_DATA_DIR / "products_cl.csv",
    orders_input: Path = INTERIM_DATA_DIR / "orders_cl.csv",
    orderlines_input: Path = INTERIM_DATA_DIR / "orderlines_cl.csv",
    brands_input: Path = INTERIM_DATA_DIR / "brands_cl.csv",
    
    # Output files - using CCDS path structure (to processed data)
    orders_output: Path = PROCESSED_DATA_DIR / "orders.csv",
    orderlines_output: Path = PROCESSED_DATA_DIR / "orderlines.csv",
    products_output: Path = PROCESSED_DATA_DIR / "products.csv",
    brands_output: Path = PROCESSED_DATA_DIR / "brands.csv",
    full_df_output: Path = PROCESSED_DATA_DIR / "full_df.csv",
    clean_df_output: Path = PROCESSED_DATA_DIR / "clean_df.csv",
):
 
    
    logger.info("Starting data quality checks...")
    
    # Read in the cleaned data using CCDS paths
    logger.info("Reading cleaned data files...")
    products = pd.read_csv(products_input)
    orders = pd.read_csv(orders_input, parse_dates=['created_date'])
    orderlines = pd.read_csv(orderlines_input, parse_dates=['date'])
    brands = pd.read_csv(brands_input)
    
    logger.info("Data quality checks in progress...")

    ### Check the consistency of keys between tables==============================================================================================

    # Set intersection of orders and orderlines
    logger.info("Checking key consistency between orders and orderlines...")
    common_ids = set(orders.order_id) & set(orderlines.order_id)
    orders_qu = orders[orders.order_id.isin(common_ids)]
    orderlines_qu = orderlines[orderlines.order_id.isin(common_ids)]
    logger.info(f"Found {len(common_ids)} common order IDs")

    # Set intersection of products and orderlines
    logger.info("Checking key consistency between products and orderlines...")
    common_ids = set(orderlines_qu.sku) & set(products.sku)

    # Find the orders with a missing product by finding the rows in the orderline table and then the set of orders associated with this
    affected_orders = set(orderlines[~orderlines.sku.isin(common_ids)].order_id)
    logger.info(f"Found {len(affected_orders)} orders with missing products")

    # Remove these orders from the orders and orderlines tables
    orders_qu = orders_qu[~orders_qu.order_id.isin(affected_orders)]
    orderlines_qu = orderlines_qu[~orderlines_qu.order_id.isin(affected_orders)]
    logger.info(f"Removed affected orders, remaining: {len(orders_qu)} orders, {len(orderlines_qu)} orderlines")

    ### Check numerical consistency between tables==============================================================================================

    logger.info("Checking numerical consistency...")
    # Add new column for revenue: quantity * price
    orderlines_qu['revenue'] = orderlines_qu.unit_price * orderlines_qu.product_quantity
    
    # Group orderlines by order_id to find total paid per order
    orderlines_grped = orderlines_qu.groupby('order_id', as_index=False)['revenue'].sum()
    
    # Merge this back into the orders table to compare against total_paid from this column
    compare_df = orders_qu.merge(orderlines_grped, on='order_id')
    
    # Calculate the difference between the two measures
    compare_df['diff'] = compare_df.total_paid - compare_df.revenue

    # Flag any differences outside of a certain tolerance
    compare_df['suspicious'] = ~(compare_df['diff'].between(-1, 20))
    
    # Find all order ids with suspicious orders
    suspicious_ids = set(compare_df[compare_df.suspicious].order_id)
    logger.info(f"Found {len(suspicious_ids)} suspicious orders outside tolerance")

    # Produce final tables
    orders_final = orders_qu[~orders_qu.order_id.isin(suspicious_ids)]
    orderlines_final = orderlines_qu[~orderlines_qu.order_id.isin(suspicious_ids)]
    logger.info(f"Final tables: {len(orders_final)} orders, {len(orderlines_final)} orderlines")

    ### Write final tables to processed data folder for use ========================================================================================
    logger.info("Writing final processed tables...")
    orderlines_final.to_csv(orderlines_output, index=False)
    logger.success(f"Orderlines saved to {orderlines_output}")
    
    orders_final.to_csv(orders_output, index=False)
    logger.success(f"Orders saved to {orders_output}")

    # Add products and brands to processed folder despite no changes
    products.to_csv(products_output, index=False)
    logger.success(f"Products saved to {products_output}")
    
    brands.to_csv(brands_output, index=False)
    logger.success(f"Brands saved to {brands_output}")

    ### Create a fully merged table and add calculated columns for data processing
    logger.info("Creating fully merged table...")
    # Merge orders and orderlines
    merge1 = orderlines_final.merge(orders_final, on='order_id')

    # Add brand name to products
    products['short'] = products.sku.str.slice(stop=3)
    products = products.merge(brands, on='short')

    # Merge products to orders and lines
    full_df = merge1.merge(products, on='sku')
    logger.info(f"Full merged table shape: {full_df.shape}")

    #Create price category column
    bin_edges = [0, 20, 100, 500, 1000, 1e25]
    bin_labels = ['0-20', '20-100', '100-500', '500-1000', 'Above 1000']
    full_df['price_category'] = pd.cut(full_df.price, bins=bin_edges, labels=bin_labels)

    #Set states that we will use in the analysis
    included_states = ['Completed', 'Pending', 'Place Order']

    #Add new columns for discounts and log columns
    full_df['discount'] = full_df.price - full_df.unit_price
    full_df['discount_per'] = full_df.discount/full_df.price * 100
    full_df['ln_quantity'] = np.log (full_df.product_quantity)
    full_df['ln_price'] = np.log (full_df.unit_price)
    full_df['ln_discount'] = np.log (full_df.discount)

    # Write this full merged dataframe to the data folder
    full_df.to_csv(full_df_output, index=False)
    logger.success(f"Full merged dataset saved to {full_df_output}")

    #Remove negative discounts and add only included states
    clean_df = full_df[(full_df.state.isin(included_states)) & (full_df.discount > -0.05)]

    logger.info(f"Full cleaned table shape: {clean_df.shape}")

    #Add cleaned_df to the data folder
    clean_df.to_csv(clean_df_output,index=False)
    logger.success(f"Full cleaned dataset saved to {clean_df_output}")

    logger.success("Data quality checks and processing completed successfully!")


if __name__ == "__main__":
    app()