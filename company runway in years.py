'''
08/25/2024: Changed cash source from qtr bal sheet from cash cash eqv short term inv to cash and cash eqv
'''


import yfinance as yf

def calculate_cash_runway(symbol):
    stock = yf.Ticker(symbol)
    

    # Retrieve quarterly income statement
    qtr_cashflow = stock.quarterly_cashflow.T
    print(qtr_cashflow)

    # Retrieve quarterly balance sheet
    qtr_bal_sheet = stock.quarterly_balance_sheet.T
    print(qtr_bal_sheet)

    # Retrieve Cash and Cash Eqv
    cash = qtr_bal_sheet['Cash And Cash Equivalents'].iloc[0]
    print("Total Cash:", cash)
    
    
    # Calculate TTM CF
    ttm_CF = qtr_cashflow['Free Cash Flow'].iloc[:4].sum()
    print("TTM Free Cash Flow:", ttm_CF)

    # Calculate # of years cash runway
    runway_years = cash / ttm_CF * -1

    if runway_years < 0:
        return print(f"{symbol} is cashflow positive")
    else: 
        return print(f"Company runway in years for {symbol}: {runway_years}")

# Example usage
symbol = 'SMCI'
calculate_cash_runway(symbol)

