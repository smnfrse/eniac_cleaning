"""
A python script for cleaning the data, it is based on the data_cleaning script in the scripts folder conmverted
into the CCDS data structure
"""

from pathlib import Path

from loguru import logger
import pandas as pd
import typer

from Smn.config import INTERIM_DATA_DIR, RAW_DATA_DIR
from Smn.utils import clean_double_decimal

app = typer.Typer()


@app.command()
def main(
    # Input files - using CCDS path structure
    orders_input: Path = RAW_DATA_DIR / "orders.csv",
    orderlines_input: Path = RAW_DATA_DIR / "orderlines.csv",
    brands_input: Path = RAW_DATA_DIR / "brands.csv",
    products_input: Path = RAW_DATA_DIR / "products.csv",
    # Output files - using CCDS path structure
    brands_output: Path = INTERIM_DATA_DIR / "brands_cl.csv",
    orders_output: Path = INTERIM_DATA_DIR / "orders_cl.csv",
    orderlines_output: Path = INTERIM_DATA_DIR / "orderlines_cl.csv",
    products_output: Path = INTERIM_DATA_DIR / "products_cl.csv",
):
    """Clean and process orders, orderlines, brands, and products data."""

    logger.info("Starting data cleaning process...")

    # Read in the raw data using CCDS paths
    logger.info("Reading raw data files...")
    orders_raw = pd.read_csv(orders_input)
    orderlines_raw = pd.read_csv(orderlines_input)
    brands_raw = pd.read_csv(brands_input)
    products_raw = pd.read_csv(products_input)

    # Cleaning brands table===========================================================================
    logger.info("Cleaning brands table...")
    brands = brands_raw.copy().convert_dtypes()
    # Save to csv using CCDS path
    brands.to_csv(brands_output, index=False)
    logger.success(f"Brands data saved to {brands_output}")

    # Cleaning orders table===========================================================================
    logger.info("Cleaning orders table...")
    # Drop NA values from the orders table
    orders = orders_raw.copy().dropna(axis=0).convert_dtypes()
    # Change date in orders table to datetime
    orders.created_date = pd.to_datetime(orders.created_date)
    # Save to csv using CCDS path
    orders.to_csv(orders_output, index=False)
    logger.success(f"Orders data saved to {orders_output}")

    # Cleaning orderlines table===========================================================================
    logger.info("Cleaning orderlines table...")
    # Make date a date type
    orderlines = orderlines_raw.copy().convert_dtypes()
    orderlines["date"] = pd.to_datetime(orderlines["date"])
    # Remove double decimals from orderlines unit price
    orderlines = clean_double_decimal(orderlines, ["unit_price"])
    # Convert unit price to numeric
    orderlines["unit_price"] = pd.to_numeric(orderlines["unit_price"])
    # Remove the useless product_id column
    orderlines.drop("product_id", axis=1, inplace=True)
    # Rename order_id for better merging
    orderlines.rename({"id_order": "order_id"}, inplace=True, axis=1)
    # Save the cleaned data to a csv file using CCDS path
    orderlines.to_csv(orderlines_output, index=False)
    logger.success(f"Orderlines data saved to {orderlines_output}")

    # Cleaning products table===========================================================================
    logger.info("Cleaning products table...")
    # Drop duplicates from the products table and autoupdate data types
    products = products_raw.copy().drop_duplicates().convert_dtypes()
    # Drop missing values from the price column (but not missing descriptions or types)
    products.dropna(subset="price", inplace=True)
    # drop promo price
    products.drop("promo_price", axis=1, inplace=True)
    # Run custom function
    products = clean_double_decimal(products, ["price"])
    # Remove questionable lines with three decimals after the point
    products = products[~(products.price.astype(str).str.contains(r"\.\d{3}$"))]
    # Change the price to numeric
    products[["price"]] = products[["price"]].astype(float)

    ### Add number of times each product has been sold from the orderlines table to product table
    prod_times_sold = orderlines.groupby("sku", as_index=False).agg(times_sold=("sku", "size"))
    products = products.merge(prod_times_sold, on="sku", how="left")

    products.to_csv(products_output, index=False)
    logger.success(f"Products data saved to {products_output}")

    logger.success("Data cleaning completed successfully!")


if __name__ == "__main__":
    app()
