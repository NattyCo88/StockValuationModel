# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 18:21:38 2024

@author: Nathan Lim
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import pycountry
import difflib
import tkinter as tk
from tkinter import simpledialog

# Global Variables
r_f_r = 0.1
years = 5 
min_market_cap = 1e9


class StockData:
    def __init__(self):
        self.stock = None
        self.income_statement = None
        self.balance_sheet = None
        self.qtr_balance_sheet = None
        self.qtr_income_statement = None
        self.income_df = None
        self.balance_df = None
        self.income_bal_merged = None
        self.qtr_balance_df = None
        self.qtr_income_df = None
        self.qtr_income_bal_merged = None
        self.latest_revenue = None
        self.latest_share_count = None
        self.latest_revenue_growth = None
        self.latest_shares_change = None
        self.latest_FDSO = None

        
     # Function to get user input
    def get_user_input_ticker(self):
         root = tk.Tk()
         root.withdraw()  # Hide the root window

         # Get Ticker
         self.ticker = simpledialog.askstring("Input", "Enter Ticker Symbol:", initialvalue='CRWD')
         
         # Initialize the stock object with the ticker symbol
         self.stock = yf.Ticker(self.ticker)

         root.destroy()
         
         
         return self.ticker, self.stock

         # Function to get user input

    def get_user_input_variables(self):
         root = tk.Tk()
         root.withdraw()  # Hide the root window

         # Get Exit Price Multiple
         self.Exit_Price_Multiple = simpledialog.askfloat("Input", "Enter Exit Price Multiple:", initialvalue=15)

         # Get FCF Margin
         self.fcf_margin = simpledialog.askfloat("Input", "Enter FCF Margin:", initialvalue=0.30)

         # Get Growth Decline
         self.growth_decl = simpledialog.askfloat("Input", "Enter Growth Decline:", initialvalue=0.10)

         root.destroy()
         
         
         return self.Exit_Price_Multiple, self.fcf_margin, self.growth_decl   
     
    def get_financials(self):
        

        try:
            self.income_statement = self.stock.financials
            self.balance_sheet = self.stock.balance_sheet
            self.qtr_income_statement = self.stock.quarterly_financials
            self.qtr_balance_sheet = self.stock.quarterly_balance_sheet
        except Exception as e:
            print(f"Error retrieving financial data: {e}")
            self.income_statement, self.balance_sheet, self.qtr_balance_sheet, self.qtr_balance_sheet = None, None, None, None

    def process_dataframes(self):
        if self.income_statement is not None and self.balance_sheet is not None and self.qtr_income_statement is not None and self.qtr_balance_sheet is not None:
           
            # Annual
            self.income_df = pd.DataFrame(self.income_statement).T
            self.balance_df = pd.DataFrame(self.balance_sheet).T

            self.income_df.reset_index(inplace=True)
            self.balance_df.reset_index(inplace=True)

            self.income_df.rename(columns={'index': 'Year'}, inplace=True)
            self.balance_df.rename(columns={'index': 'Year'}, inplace=True)

            self.income_df['Year'] = pd.to_datetime(self.income_df['Year']).dt.strftime('%Y-%m-%d')
            self.balance_df['Year'] = pd.to_datetime(self.balance_df['Year']).dt.strftime('%Y-%m-%d')

            self.income_df.set_index('Year', inplace=True)
            self.balance_df.set_index('Year', inplace=True)

            self.income_df.sort_index(inplace=True)
            self.balance_df.sort_index(inplace=True)

            self.income_bal_merged = pd.merge(self.income_df, self.balance_df, left_index=True, right_index=True)
            
            # QTR
            self.qtr_income_df = pd.DataFrame(self.qtr_income_statement).T
            self.qtr_balance_df = pd.DataFrame(self.qtr_balance_sheet).T

            self.qtr_income_df.reset_index(inplace=True)
            self.qtr_balance_df.reset_index(inplace=True)

            self.qtr_income_df.rename(columns={'index': 'Year'}, inplace=True)
            self.qtr_balance_df.rename(columns={'index': 'Year'}, inplace=True)

            self.qtr_income_df['Year'] = pd.to_datetime(self.qtr_income_df['Year']).dt.strftime('%Y-%m-%d')
            self.qtr_balance_df['Year'] = pd.to_datetime(self.qtr_balance_df['Year']).dt.strftime('%Y-%m-%d')

            self.qtr_income_df.set_index('Year', inplace=True)
            self.qtr_balance_df.set_index('Year', inplace=True)

            self.qtr_income_df.sort_index(inplace=True)
            self.qtr_balance_df.sort_index(inplace=True)

            self.qtr_income_bal_merged = pd.merge(self.qtr_income_df, self.qtr_balance_df, left_index=True, right_index=True)  

    def display_data(self):
        if self.income_bal_merged is not None and self.qtr_income_bal_merged is not None:
            # Set pandas option to display all columns
            pd.set_option('display.max_columns', None)
            
            #print("List of Variables from Merged Annual Inc and Bal Sheet:")
            #print(list(self.income_bal_merged.columns))
            
            #print("\nList of Variables from Merged Qtr Inc and Bal Sheet:")
            #print(list(self.qtr_income_bal_merged.columns))

            revenue = self.income_bal_merged['Total Revenue']
            FDSO_shares = self.qtr_income_bal_merged['Share Issued']
            shares = self.income_bal_merged['Share Issued']
            
            self.latest_revenue = revenue.iloc[-1]
            self.latest_share_count = FDSO_shares.iloc[-1]
            print(f"Latest Revenue: {self.latest_revenue}")
            print(f"\nLatest FDSO: {self.latest_share_count}")

            pd.set_option('future.no_silent_downcasting', True)
            
            revenue_growth = revenue.pct_change() * 100
            shares_change = shares.pct_change() * 100

            print("\nYear-over-Year Revenue Growth (%):")
            print(revenue_growth)
            print("\nYear-over-Year Change in Number of Shares (%):")
            print(shares_change)

            self.latest_revenue_growth = revenue_growth.iloc[-1] / 100
            self.latest_shares_change = shares_change.iloc[-1] / 100

            print("\nLatest Year-over-Year Revenue Growth (%):", self.latest_revenue_growth*100)
            print("\nLatest Year-over-Year Change in Number of Shares (%):", self.latest_shares_change*100)

    def calculate_share_valuation(self):
        if self.latest_revenue is None or self.latest_share_count is None or self.latest_revenue_growth is None or self.latest_shares_change is None:
            print("Financial data is not available. Please run the display_data method first.")
            return None
        
        growth_rates = [self.latest_revenue_growth * (1 - self.growth_decl * (i+1)) for i in range(years)]
        print("\nRevenue Growth Rates:", growth_rates)
        
        projected_revenues = []
        current_revenue = self.latest_revenue
        for rate in growth_rates:
            current_revenue *= (1 + rate)
            projected_revenues.append(current_revenue)
        print("\nProjected Revenues:", projected_revenues)
        
        projected_fcf = [rev * self.fcf_margin for rev in projected_revenues]
        print("\nProjected FCF:", projected_fcf)
        
        disc_fcf = [fcf / (1 + r_f_r) ** (c + 1) for fcf, c in zip(projected_fcf, range(years))]
        print("\nDisc FCF:", disc_fcf)
        
        projected_share_count = [self.latest_share_count * ((1 + self.latest_shares_change) ** a) for a in range(years)]
        print("\nProjected Share Count:", projected_share_count)
        
        disc_fcf_per_share = [fcf / share_count for fcf, share_count in zip(disc_fcf, projected_share_count)]
        disc_fcf_per_share = pd.Series(disc_fcf_per_share)
        disc_fcf_per_share = pd.to_numeric(disc_fcf_per_share, errors='coerce')
        print("\nDiscounted FCF per Share:", disc_fcf_per_share)
        
        accum_fcf_per_share = np.sum(disc_fcf_per_share)
        print("\nAccum FCF per share:\n", accum_fcf_per_share)
        
        final_valuation = disc_fcf_per_share.iloc[-1] * self.Exit_Price_Multiple + accum_fcf_per_share
        
        return print(f"{self.ticker} Valuation: {final_valuation}")
    
    '''
    def get_country_code(self, country_name):
        try:
            return print(pycountry.countries.lookup(country_name).alpha_2)
        except LookupError:
            return 'N/A'
    '''
    
    # Manual intervention to rename industry categories (YF != financialmodelingprep API)
    def rename_industry(self, industry):
        # Dictionary to map original industry names to desired names
        industry_rename_map = {
            'Internet Retail': 'Specialty Retail'
            #Add more mappings as needed
        }
        return industry_rename_map.get(industry, industry)
    
    def get_stock_industries(self):
        # Get the stock info
        stock = yf.Ticker(self.ticker)
        industry = stock.info.get('industry', 'N/A')
        sector = stock.info.get('sector', 'N/A')
        country_name = stock.info.get('country', 'N/A')
        
        # Rename the industry if it matches any in the rename map
        industry = self.rename_industry(industry)

        # Create a list of industries and sectors
        self.industries = [industry]
        self.sectors = [sector]
        print(industry)
        # Rename certain industry
        return self.industries, self.sectors
    
    def get_similar_companies(self, min_market_cap):
        self.industries, self.sectors = self.get_stock_industries()
        
        # Use a public API to get similar companies (e.g., Financial Modeling Prep API)
        api_key = '7pugWlEq68qVYPYdUJFGXFKGAC95iyPI'  # Replace with your API key
        
        for ind, sec in zip(self.industries, self.sectors):
            url = f'https://financialmodelingprep.com/api/v3/stock-screener?sector={sec}&apikey={api_key}'
            if min_market_cap:
                url += f'&marketCapMoreThan={min_market_cap}'
            response = requests.get(url)
            data = response.json()
            self.similar_companies = []
            for company in data:
                if company['symbol'] != self.ticker:
                    self.similar_companies.append(company)
                    
        # Filter companies that belong to all specified industries and meet additional criteria
        filtered_companies = []
        for company in self.similar_companies:
            self.company_industries = [company['industry'], company['sector']]
            if all(ind in self.company_industries for ind in self.industries):
                if min_market_cap and company['marketCap'] < min_market_cap:
                    continue
                filtered_companies.append(company)
        
        # Sort the filtered companies by market capitalization
        sorted_companies = sorted(filtered_companies, key=lambda x: x['marketCap'], reverse=True)
        
        # Create a dictionary of stock tickers and company names
        company_dict = {company['symbol']: company['companyName'] for company in sorted_companies}
        
        # Remove repeated companies by comparing stock tickers and remove those >80% similar ticker names
        self.unique_companies = {}
        for symbol, name in company_dict.items():
            # Check for similar names
            if not any(difflib.SequenceMatcher(None, name, existing_name).ratio() > 0.8 for existing_name in self.unique_companies.values()):
                self.unique_companies[symbol] = name
            if len(self.unique_companies) == 10:
                break
        
        return print(f"Top 10 companies similar to {self.ticker}: {self.unique_companies}")

    # Calculate P/S Ratio for Companies similar to desired stock
    def get_ps_ratios(self):

        self.ps_ratios = {}

        for symbol in self.unique_companies.keys():
            try:
                stock = yf.Ticker(symbol)
                market_cap = stock.info.get('marketCap', 'N/A')
                financials = stock.quarterly_financials
                ttm_revenue = financials.loc['Total Revenue'].iloc[:4].sum()
                
                if market_cap != 'N/A' and ttm_revenue != 'N/A' and ttm_revenue != 0:
                    self.ps_ratios[symbol] = market_cap / ttm_revenue
                else:
                    self.ps_ratios[symbol] = 'N/A'
            except Exception as e:
                self.ps_ratios[symbol] = f"Error: {e}"

        print(f"P/S Ratios for similar companies: {self.ps_ratios}")
        return self.ps_ratios

''' 
Add in Feature for forward valuation based on 5th year and potential upside and yearly CAGR
'''

stock_data = StockData()
stock_data.get_user_input_ticker()
stock_data.get_stock_industries()
stock_data.get_similar_companies(min_market_cap)
stock_data.get_ps_ratios()
stock_data.get_user_input_variables()
stock_data.get_financials()
stock_data.process_dataframes()
stock_data.display_data()
stock_data.calculate_share_valuation()



