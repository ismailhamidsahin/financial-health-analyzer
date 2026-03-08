import yfinance as yf
import pandas as pd
from google import genai # NEW: Updated library import

# 1. Setup the AI (Keep your API key inside the quotes!)
API_KEY = "insert your api key here"

# NEW: The new way to initialize the AI client
client = genai.Client(api_key=API_KEY)

def analyze_financials(ticker_symbol):
    print(f"Fetching data for {ticker_symbol}...")
    stock = yf.Ticker(ticker_symbol)
    
    income_stmt = stock.financials
    balance_sheet = stock.balance_sheet
    
    if income_stmt.empty or balance_sheet.empty:
        print(f"Error: Could not fetch data for {ticker_symbol}.")
        return
        
    print("✅ Data fetched! Calculating ratios...\n")
    
    try:
        # Extract Items
        current_assets = balance_sheet.loc["Current Assets"].iloc[0]
        current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0]
        net_income = income_stmt.loc["Net Income"].iloc[0]
        total_revenue = income_stmt.loc["Total Revenue"].iloc[0]
        
        # Calculate Ratios
        current_ratio = current_assets / current_liabilities
        profit_margin = (net_income / total_revenue) * 100
        
        print(f"--- Key Metrics for {ticker_symbol} ---")
        print(f"Current Ratio: {current_ratio:.2f}")
        print(f"Profit Margin: {profit_margin:.2f}%")
        
        # --- Phase 3 - AI Interpretation ---
        print("\n🤖 Asking AI for interpretation...")
        
        prompt = f"""
        You are an expert financial analyst. I am providing you with the latest financial metrics for the stock ticker {ticker_symbol}.
        
        - Current Ratio: {current_ratio:.2f}
        - Profit Margin: {profit_margin:.2f}%
        
        Based strictly on these numbers, write a short, 3-sentence analysis of the company's liquidity (current ratio) and profitability (profit margin). Keep it professional and simple.
        """
        
        # NEW: The updated way to call the newest Gemini model
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # Print the AI's response!
        print("\n=== AI Financial Analysis ===")
        print(response.text)
        print("=============================\n")
        
    except KeyError as e:
        print(f"Error: Could not find the specific accounting line item: {e}")

# Run the test
if __name__ == "__main__":
    analyze_financials("AAPL")