import yfinance as yf

def calculate_ev_nopat_ratio(symbol):
    """
    Calculate the EV/NOPAT ratio for a given stock symbol.

    Args:
        symbol (str): The stock symbol.

    Returns:
        float: The EV/NOPAT ratio.
    """
    stock = yf.Ticker(symbol)
    
    # Retrieve market cap
    market_cap = stock.info.get('marketCap', 'N/A')

    # Retrieve quarterly income statement
    qtr_income_stmt = stock.quarterly_financials.T
    print(qtr_income_stmt)
    # Retrieve quarterly balance sheet
    qtr_bal_sheet = stock.quarterly_balance_sheet.T
    print(qtr_bal_sheet)

    # Retrieve Total Debt
    total_debt = qtr_bal_sheet['Total Debt'].iloc[0]
    print("Total Debt:", total_debt)
    # Retrieve Cash, Cash Eqv and Short Term Investments
    cash = qtr_bal_sheet['Cash Cash Equivalents And Short Term Investments'].iloc[0]
    print("Total Cash:", cash)
    # Calculate Enterprise Value (EV)
    if market_cap != 'N/A' and total_debt != 'N/A' and cash != 'N/A':
        ev = market_cap + total_debt - cash
        print("EV:", ev)
    else:
        return 'N/A'
    
    
    # Calculate TTM Operating Income (EBIT)
    ttm_ebit = qtr_income_stmt['EBIT'].iloc[:4].sum()
    print("EBIT:", ttm_ebit)
    
    # Calculate TTM Tax Expense
    ttm_tax_rate = qtr_income_stmt['Tax Rate For Calcs'].iloc[:4].mean()
    print("TTM Tax Rate:", ttm_tax_rate)

    # Calculate NOPAT
    nopat = ttm_ebit * (1 - ttm_tax_rate)
    print("NOPAT:", nopat)
    
    # Calculate EV/NOPAT ratio
    if nopat != 0:
        ev_nopat_ratio = ev / nopat
    else:
        ev_nopat_ratio = 'N/A'
    
    return ev_nopat_ratio

# Example usage
symbol = 'MU'
ev_nopat_ratio = calculate_ev_nopat_ratio(symbol)

print(f"EV/NOPAT ratio for {symbol}: {ev_nopat_ratio}")
