# Eniac - Data Cleaning and Storytelling

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

## Case Study: Eniac's Discount Strategy

You will keep working for Eniac -the e-commerce tech company- as a Data Analyst. This time you will work with internal data, which is not anonymised… but a bit more chaotic! The company has high hopes put into the possibilities that come with Data Analysis, and they are especially hopeful that your work can finally settle an ongoing debate: whether or not it's beneficial to discount

## Reproducing the project

The project pipeline can either be run using make, or manually. To get a full list of make commands you can use $ make

**Using Make:**
```bash
$ make environment
$ conda activate eniac_cleaning
$ make pipeline
```

**Manual setup:**
```bash
$ conda env create -f environment.yml
$ conda activate eniac_cleaning
$ python -m Smn.data_cleaning
$ python -m Smn.data_quality
$ python -m Smn.plots
```

## Project Organization

```
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── notebooks          <- Jupyter notebooks.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         Smn and configuration for tools like black
│
├── figures            <- Generated graphics and figures to be used in reporting
│
├── environment.yml    <- Requirements to set up a virtual environment
│
└── Smn                <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes Smn a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── data_cleaning.py        <- Downloads and cleans data and outputs csv files in the data/interim folder
    │
    ├── data_quality.py         <- Checks data quality, adds calculated columns, and outputs csv files to data/processed folder
    │
    ├── plots.py                <- Code that outputs final plots in the figures folder
    │
    └── utils.py                <- Code containing functions used in the other scripts
```

--------