import pandas as pd
import numpy as np
import statsmodels.api as sm
#import linearmodels as lm 
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# Function that can remove the first decimal from a number (formatted as a string), when there are two
def clean_double_decimal(df: pd.DataFrame, cols: list):
    for col in cols:
        mask = df[col].str.count(r'\.') > 1
        df.loc[mask, col] = df.loc[mask, col].str.replace(r'\.', '', n=1, regex=True)
    return df

#see doc string
def group_elasticities(df: pd.DataFrame, group_col: list, freq: str, date_col='date', discount_col='discount', sales_col='product_quantity'):
    """This function calculates the elasticities, i.e. the log-log relationship between discount and quantity
    df: a pandas dataframe containing data
    freq: time frequency used by resample
    group_cols: a list of columns to be grouped, the elasticity will then be calculated for each intersection of this list
    date_col: date used for resample
    discount_col: column name of the discount column
    sales_col: column name for the sales or quantity column"""
    grouped_df = _group_nlog(df, group_col, freq, date_col, discount_col, sales_col)
    elasticies_df = _elasticity_calc(grouped_df, group_col)
    return elasticies_df

#Helper for group elasticities #1: Resample the dataframe and calculate columns needed for elasticity calculations
def _resample_nlog(df, freq='d', date_col='date', discount_col='discount', sales_col='product_quantity'):
    resample_df = (df.resample(freq, on=date_col)
                     .agg(sales=(sales_col, 'sum'), 
                          price=('unit_price', 'mean'), 
                          discount=(discount_col, 'mean'),
                          include_groups=False)
                    #.reset_index()
                    )
    resample_df['log_sales'] = np.log(resample_df['sales'] + 1) 
    resample_df['log_discount'] = np.log(resample_df['discount'] + 1)
    return(resample_df)

#Helper for group elasticities #2: Run the resmpled function using a grouping
def _group_nlog (df: pd.DataFrame, group_col: str, freq='d', date_col='date', discount_col='discount', sales_col='product_quantity'):
    grouped_df = _resample_nlog(df.groupby(group_col), freq).reset_index()
    return grouped_df

#Helper for group elasticities #3: Calculate the elasticities accross the groups
def _elasticity_calc(df, group_col):
    elasticities_df = pd.DataFrame(columns=[group_col, 'Elasticity', 'P_value', 'Revenue', 'Sales', 'Average_Price', 'Total_Discount'])
    df['revenue'] = df.price * df.sales
    for i in df[group_col].unique():
        subset = df[df[group_col] == i].dropna()
        X = subset[['log_discount']]
        y = subset['log_sales']
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        #Calculate information about each group
        revenue = subset.revenue.sum()
        sales = subset.sales.sum()
        mn_price = revenue/sales
        discount = subset.discount.sum()
        elasticities_df.loc[len(elasticities_df)] = [i, model.params.log_discount, model.pvalues.log_discount, revenue, sales, mn_price, discount]
    return elasticities_df

#Function to group data
def group_nlog (df: pd.DataFrame, group_cols: list):
    grouped_df = resample_nlog(df.groupby(group_cols))
    return grouped_df

#Resamples dataframe for frequency and calculates aggregates needed for calculating elasticities
def resample_nlog(df, freq='d'):
    resample_df = (df.resample(freq, on='date')
                     .agg(sales=('product_quantity', 'sum'), 
                          price=('unit_price', 'mean'), 
                          discount=('discount', 'mean'))
                    #.reset_index()
                    )
    resample_df['log_sales'] = np.log(resample_df['sales'] + 1) 
    resample_df['log_discount'] = np.log(resample_df['discount'] + 1)
    return(resample_df)

# #Conducts a fixed effects regression
# def fixed_reg(df):
#     model = lm.PanelOLS.from_formula(
#     'log_sales ~ log_discount + EntityEffects', 
#     data=df
#     )
#     results = model.fit()
#     return results

#Formats a scatter plot showing the relationship between discounts and sales
def plot_nformat(df, save_path=None):
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        df['log_discount'], df['log_sales']
    )

    sns.set_style("whitegrid")
    
    # Create figure and axis explicitly
    fig, ax = plt.subplots(figsize=(10, 5.6))
    
    sns.regplot(
        data=df,
        x='log_discount', 
        y='log_sales',
        scatter_kws={'alpha': 0.6, 's': 60, 'color': 'steelblue'},
        line_kws={'color': 'red', 'linewidth': 2},
        ci=95,
        ax=ax
    )
    
    ax.set_title(f'Log Discount vs Log Sales\n'
                 f'y = {intercept:.3f} + {slope:.3f}x (R²={r_value**2:.3f})')
    fig.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)  # Close to prevent display
    
    return fig

def create_lags (df, nlags, col_name):
    for n in range(1, nlags + 1):
        df[col_name + '_lag' + str(n)] = df[col_name].shift(n)
    return(df.dropna())

def bar_plot(df, x_col, y_col, group_name, nlarg_col, nlarg_num=10):
    """Creates a barplot and applies formatting"""
    # Sort by elasticity and prepare data
    sorted_data = df.nlargest(nlarg_num, nlarg_col).sort_values(x_col, ascending=False)

    # Create the plot with color representing revenue on log scale
    fig, ax = plt.subplots(figsize=(10, 5.625))

    # Create the barplot
    sns.barplot(data=sorted_data,
                x=x_col,
                y=y_col,
                hue=y_col,
                edgecolor='black',
                linewidth=0.5,
                ax=ax)

    # Create custom colors based on revenue (log scale)
    from matplotlib.colors import LogNorm

    # Get revenue values and apply log scale
    revenues = sorted_data[nlarg_col].values
    log_revenues = np.log10(revenues)  # Log transform

    # Normalize for colormap
    norm = LogNorm(vmin=revenues.min(), vmax=revenues.max())
    cmap = plt.cm.viridis

    # Update bar colors based on revenue
    for i, bar in enumerate(ax.patches):
        bar.set_facecolor(cmap(norm(revenues[i])))

    # Customize the plot using ax instead of plt
    ax.set_title(f'{x_col} - Top {nlarg_num} {group_name} by {nlarg_col}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(x_col, fontsize=12, fontweight='bold')
    ax.set_ylabel(group_name, fontsize=12, fontweight='bold')

    # Add value labels on bars
    for i, (v, rev) in enumerate(zip(sorted_data[x_col], sorted_data[nlarg_col])):
        ax.text(v + 0.01 * (1 if v >= 0 else -1), i, 
                f'{v:.2f}', 
                va='center', 
                fontweight='bold')

    # Add vertical line at x=0 for reference
    ax.axvline(x=0, color='red', linestyle='--', alpha=0.7, linewidth=1)

    # Add colorbar to show revenue scale
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.8)
    cbar.set_label(nlarg_col, fontsize=10, fontweight='bold')

    # Adjust layout and aspect ratio
    sns.despine(left=True, bottom=True)
    fig.tight_layout()
    
    # Set aspect ratio to match the figure size ratio (10/5.625 ≈ 1.78)
    ax.set_aspect(1.0 / ax.get_data_ratio() * (5.625/10))
    
    return fig

#Function to create and format a scatter plot
def scatter_plot(df, x_col, y_col, hue_col, group_name, label_col = None, loc = 'upper right'):
    """"Creates a scatter plot and transforms using formatting for this project"""
# Create plot with log-transformed revenue
    g = sns.relplot(
        data=df,
        x=x_col,
        y=y_col,
        size=np.log10(df[hue_col]),
        hue=np.log10(df[hue_col]),
        palette='viridis',
        alpha=0.7
    )

    # Add title and labels
    g.figure.suptitle(f'{y_col.replace('_', ' ')} vs {x_col.replace('_', ' ')} by {group_name.replace('_', ' ')}', fontsize=14, fontweight='bold', y=1.02)
    g.set_axis_labels('Average Price ($)', 'Price Elasticity')
    g.figure.set_size_inches(10, 5.6)

    # Get top brands for labeling
    top_brands = df.nlargest(6, hue_col)

    # Add labels
    if label_col is not None:
        for idx, row in top_brands.iterrows():
            g.ax.text(
                row[x_col] + 0.02,
                row[y_col] + 0.02,
                row[label_col],
                fontsize=9,
                alpha=0.8
            )

    # Improve styling
    g.ax.grid(True, alpha=0.3)
    g.ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)

    # Update legend labels to show actual revenue values
    if g._legend:
        # Get current legend handles and labels
        handles, labels = g.ax.get_legend_handles_labels()
        # Convert log values back to readable revenue numbers
        new_labels = [f"${float(label)**10:,.0f}" for label in labels]
        g.ax.legend(
                handles, 
                new_labels, 
                title=hue_col,
                loc=loc,  # Or choose another location: 'upper left', 'lower right', etc.
                frameon=False,  # Remove border
                fancybox=False,  # Remove rounded corners
                fontsize=10,
                title_fontsize=12
            )

    #g.ax.legend_.remove()
    g._legend.remove()
    
    return g
    



