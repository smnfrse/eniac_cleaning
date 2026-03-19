# Eniac - Data Cleaning and Discount Analysis

## Background

Eniac is an e-commerce tech company with an ongoing internal debate: are discounts actually good for the business? This project takes their raw transactional data — orders, order line items, products, and brands — and turns it into something clean enough to answer that question through price elasticity analysis.

## The data problem

The raw data was messy in ways that required careful handling at every step. Prices contained malformed decimals (values like `12.99.5` where an extra decimal point had crept in). The products table had duplicates and rows with missing prices. Keys didn't match cleanly across tables — some orders referenced products that didn't exist in the product catalogue, and some order line items pointed to orders that weren't in the orders table.

Even after cleaning the individual tables, reconciling them against each other revealed further problems. Comparing `total_paid` on orders against the sum of `unit_price * quantity` from the corresponding line items showed discrepancies that needed judgment calls: a tolerance window of -1 to +20 was chosen to allow for small rounding differences and likely shipping charges, while flagging anything outside that range as suspicious. Negative discounts had to be filtered, and only orders in meaningful states (Completed, Pending, Place Order) were kept.

None of these decisions had a single "correct" answer — each involved weighing what to keep against what to discard, and trying not to throw away good data along with the bad.

## Reproducing the project

The pipeline can be run using Make or manually. For a full list of Make targets:

```bash
make
```

**Using Make:**
```bash
make create_environment
conda activate eniac_cleaning
make pipeline
```

**Manual setup:**
```bash
conda env create -f environment.yml
conda activate eniac_cleaning
python -m Smn.data_cleaning
python -m Smn.data_quality
python -m Smn.plots
```

## Project Organisation

```
├── Makefile           <- Makefile with convenience commands
├── README.md
├── data
│   ├── raw            <- The original, immutable data dump.
│   ├── interim        <- Intermediate data that has been transformed.
│   └── processed      <- The final, canonical data sets for analysis.
│
├── notebooks          <- Jupyter notebooks used for exploration (not part of the pipeline)
│
├── pyproject.toml     <- Project configuration and tooling setup (Ruff, flit)
│
├── figures            <- Generated plots from the elasticity analysis
│
├── environment.yml    <- Conda environment specification
│
└── Smn                <- Source code for the data pipeline.
    ├── config.py               <- Path constants and logging configuration
    ├── data_cleaning.py        <- Cleans raw tables and outputs to data/interim
    ├── data_quality.py         <- Reconciles tables, adds calculated columns, outputs to data/processed
    ├── plots.py                <- Generates elasticity plots to figures/
    └── utils.py                <- Shared functions (cleaning, elasticity calculations, plotting)
```