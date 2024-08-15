import yfinance as yf

stock = yf.Ticker('MU')
    
# Retrieve quarterly financials
qtr_income_stmt = stock.quarterly_financials
print(qtr_income_stmt)

qtr_bal_sheet = stock.quarterly_balance_sheet
print(qtr_bal_sheet)

qtr_cashflow = stock.quarterly_cashflow
print(qtr_cashflow)

