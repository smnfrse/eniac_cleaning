from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer

from Smn.config import FIGURES_DIR, PROCESSED_DATA_DIR

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from Smn.utils import group_elasticities, resample_nlog, plot_nformat, bar_plot, scatter_plot
app = typer.Typer()


@app.command()
def main(
    input_path: Path = PROCESSED_DATA_DIR / "clean_df.csv",
    output_path: Path = FIGURES_DIR,
):
    
    logger.info("Loading data and generating first plots...")
    clean_df = pd.read_csv(input_path, parse_dates=['date', 'created_date'])
    
    # create a pooled elasticity calculation, grouped by day
    daily_df = resample_nlog(clean_df)
    plot_nformat(daily_df, output_path / "daily_pooled_elasticity.png")

    # Create a pooled elasticity calculation, grouped by week
    weekly_df = resample_nlog(clean_df, 'W')
    plot_nformat(weekly_df, output_path / "weekly_pooled_elasticity.png")

    logger.success(f"Pooled elasticity graphs saved to {output_path}")

    logger.info("Creating elasticity plots grouped by brand...")
    brand_elasticities = group_elasticities(clean_df, 'long', 'W')
    brand_elasticities_d = group_elasticities(clean_df, 'long', 'd')

    bar_plot(brand_elasticities, 'Elasticity', 'long', 'Brands', 'Revenue', 10)
    plt.savefig(output_path / "elasticity_weekly_brand_bar.png", dpi=300, bbox_inches='tight')
    plt.close()

    brand_w = scatter_plot(brand_elasticities[brand_elasticities.Sales > 1000], 'Average_Price', 'Elasticity', 'Revenue', 'Brand', 'long')
    brand_w.tight_layout()
    brand_w.savefig(output_path / "elasticity_weekly_brand_scatter.png", dpi=300, bbox_inches='tight')
    plt.close()

    # Repeat for daily grouped data
    bar_plot(brand_elasticities_d, 'Elasticity', 'long', 'Brands', 'Revenue', 10)
    plt.savefig(output_path / "elasticity_daily_brand_bar.png", dpi=300, bbox_inches='tight')
    plt.close()

    brand_d = scatter_plot(brand_elasticities_d[brand_elasticities_d.Sales > 1000], 'Average_Price', 'Elasticity', 'Revenue', 'Brand', 'long')
    brand_d.tight_layout()
    brand_d.savefig(output_path / "elasticity_daily_brand_scatter.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    
    logger.success(f"Brand elasticity graphs saved to {output_path}")

    # Group by price category
    logger.info("Creating elasticity plots grouped by price category...")
    price_cat_groups = group_elasticities(clean_df, 'price_category', 'W')
    
    bar_plot(price_cat_groups, 'Elasticity', 'price_category', 'Price Categories', 'Revenue', 10)
    plt.savefig(output_path / "elasticity_weekly_price_cat_bar.png", dpi=300, bbox_inches='tight')
    plt.close()
    logger.success("Saved weekly price category bar plot")
    
    price_cat_scatter = scatter_plot(price_cat_groups[price_cat_groups.Sales > 1000], 'Average_Price', 'Elasticity', 'Revenue', 'Price Category', 'price_category')
    price_cat_scatter.tight_layout()
    price_cat_scatter.savefig(output_path / "elasticity_weekly_price_cat_scatter.png", dpi=300, bbox_inches='tight')
    plt.close()
    logger.success("Saved weekly price category scatter plot")

    # Group by both type and price
    logger.info("Creating elasticity plots grouped by type and price...")
    clean_df['type_price'] = clean_df.type.astype(str) + '/' + clean_df.price.astype(str)
    typeprice_cat_groups = group_elasticities(clean_df, 'type_price', 'W')
    
    bar_plot(typeprice_cat_groups, 'Elasticity', 'type_price', 'Type/Price Combinations', 'Revenue', 10)
    plt.savefig(output_path / "elasticity_weekly_type_price_bar.png", dpi=300, bbox_inches='tight')
    plt.close()
    logger.success("Saved weekly type/price bar plot")
    
    typeprice_scatter = scatter_plot(typeprice_cat_groups[typeprice_cat_groups.Sales > 1000], 'Average_Price', 'Elasticity', 'Revenue', 'Type/Price', 'type_price')
    typeprice_scatter.tight_layout()
    typeprice_scatter.savefig(output_path / "elasticity_weekly_type_price_scatter.png", dpi=300, bbox_inches='tight')
    plt.close()
    logger.success("Saved weekly type/price scatter plot")

    logger.success("All plots generated successfully!")

if __name__ == "__main__":
    app()
