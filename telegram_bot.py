import pandas as pd
import os
from google import genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================================
# 1. ADD YOUR KEYS HERE
# ==========================================
GEMINI_API_KEY = "put your gemini api key here (google)"
TELEGRAM_BOT_TOKEN = "put your telegram token key here"

client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. DOCUMENT HANDLING & AI LOGIC
# ==========================================
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Acknowledge the file
    await update.message.reply_text("📥 I received your file! Reading the data and analyzing... Please wait ⏳")
    
    try:
        # 2. Download the file from Telegram to your computer
        document = update.message.document
        file_id = document.file_id
        new_file = await context.bot.get_file(file_id)
        
        file_name = document.file_name
        file_path = f"temp_{file_name}"
        await new_file.download_to_drive(file_path)
        
        # 3. Read the file using pandas
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            await update.message.reply_text("❌ Please send a valid Excel (.xlsx) or CSV (.csv) file.")
            return

        # Convert the spreadsheet into a text format the AI can read
        data_string = df.to_string()
        
        # 4. Clean up (delete the file from your computer to protect privacy)
        if os.path.exists(file_path):
            os.remove(file_path)

        # 5. Build the Prompt for Gemini
        prompt = f"""
        You are an expert financial advisor. I am providing you with my raw financial statement data from a spreadsheet.
        
        Here is the data:
        {data_string}
        
        Please do the following:
        1. Identify my Total Revenue, Net Income, Current Assets, and Current Liabilities.
        2. Calculate my Current Ratio and Profit Margin.
        3. Write a short, 3-4 sentence analysis of my financial health, liquidity, and profitability based on this data. Highlight any red flags.
        """
        
        # 6. Ask Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        # 7. Send the result back!
        await update.message.reply_markdown(response.text)
        
    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred while reading your file: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Hello! I am your Private Financial Analyst Bot. 📈\n\n"
        "Drag and drop an Excel (.xlsx) or CSV file containing your Balance Sheet or Income Statement into this chat, and I will analyze it for you!"
    )
    await update.message.reply_text(welcome_message)

# ==========================================
# 3. START THE BOT
# ==========================================
if __name__ == "__main__":
    print("Starting Telegram Bot...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    # NEW: This handler specifically listens for files/documents!
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    print("✅ Bot is online! Send it an Excel or CSV file.")
    app.run_polling()