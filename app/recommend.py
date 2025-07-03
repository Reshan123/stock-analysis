import os
import re
import httpx
from app.telegram import send_telegram_message

async def get_stock_recommendation(text: str, chat_id: int):
    parts = text.split(" ")
    if len(parts) < 2 or not parts[1].strip():
        send_telegram_message(chat_id, "<b>Error: Please provide a company symbol. Usage: /recommend SYMBOL</b>")
        return {"error": "Missing symbol"}

    symbol = parts[1].strip().upper()
    url = "https://www.cse.lk/api/companyInfoSummery"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, data={"symbol": symbol})
    
    if response.status_code != 200:
        send_telegram_message(chat_id, f"<b>Invalid stock symbol: {symbol}</b>")
        return {"error": "Invalid stock symbol"}

    company_info = response.json()
    info = company_info.get("reqSymbolInfo", {})

    if not info or not info.get("lastTradedPrice"):
        send_telegram_message(chat_id, (
            f"📡 <b>Market data for {symbol} is currently unavailable.</b>\n"
            f"🕖 This typically occurs before the Colombo Stock Exchange opens.\n"
            f"⏰ Please try again after <b>9:30 AM</b>."
        ))
        return {"error": "Market data unavailable"}

    # Create prompt
    prompt = f"""
You are a professional stock market advisor AI with expertise in analyzing Sri Lankan equities. Analyze the following real-time stock data for <b>{info['name']} ({info['symbol']})</b> and provide a concise investment recommendation.

<b>Requirements:</b>
- Use proper HTML formatting with <b>, <i>, and bullet points using • (not raw Markdown).
- If unusual volatility or market behavior is detected, include a note about it.
- Do not invent news — rely only on visible data or widely known context about the company or sector.

<b>Stock Data:</b><br>
• Company: <b>{info['name']} ({info['symbol']})</b><br>
• Current Price: <b>{info['lastTradedPrice']} LKR</b><br>
• Day High: <b>{info['hiTrade']} LKR</b><br>
• Day Low: <b>{info['lowTrade']} LKR</b><br>
• Change Today: <b>{info['change']} LKR</b><br>
• Previous Close: <b>{info['previousClose']} LKR</b><br>

<b>Output Format:</b><br>
Begin with a heading like: <b>Investment Recommendation for {info['name']} ({info['symbol']})</b><br>
Then provide the analysis, followed by a brief summary sentence.
"""

    together_payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        "messages": [{"role": "user", "content": prompt}]
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('TOGETHER_AI_API_KEY', '')}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        ai_response = await client.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=together_payload
        )

    if ai_response.status_code != 200:
        send_telegram_message(chat_id, "<b>⚠️ AI generation failed. Please try again later.</b>")
        return {"error": "AI request failed", "status_code": ai_response.status_code}

    result = ai_response.json()
    reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Clean up <think> tags if present
    reply_cleaned = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL)
    send_telegram_message(chat_id, reply_cleaned.strip())
    return {"ok": True}
