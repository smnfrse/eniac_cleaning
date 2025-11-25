import pandas as pd
import numpy as np
import statsmodels.api as sm

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

#Resample the dataframe and calculate columns needed for elasticity calculations
def _resample_nlog(df, freq='d', date_col='date', discount_col='discount', sales_col='product_quantity'):
    resample_df = (df.resample(freq, on=date_col)
                     .agg(sales=(sales_col, 'sum'), 
                          price=('unit_price', 'mean'), 
                          discount=(discount_col, 'mean'))
                    #.reset_index()
                    )
    resample_df['log_sales'] = np.log(resample_df['sales'] + 1) 
    resample_df['log_discount'] = np.log(resample_df['discount'] + 1)
    return(resample_df)

#Run the resmpled function using a grouping
def _group_nlog (df: pd.DataFrame, group_col: str, freq='d', date_col='date', discount_col='discount', sales_col='product_quantity'):
    grouped_df = _resample_nlog(df.groupby(group_col), freq).reset_index()
    return grouped_df

#Calculate the elasticities accross the groups
def _elasticity_calc(df, group_col):
    elasticities_df = pd.DataFrame(columns=[group_col, 'Elasticity', 'P_value', 'Revenue', 'Sales', 'Average_Price'])
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
        elasticities_df.loc[len(elasticities_df)] = [i, model.params.log_discount, model.pvalues.log_discount, revenue, sales, mn_price]
    return elasticities_df


