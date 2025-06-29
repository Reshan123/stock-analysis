from fastapi import FastAPI, Request
import requests
# Use a pipeline as a high-level helper
import torch
# from transformers.pipelines import pipeline

# model = pipeline(
#     task="text2text-generation",
#     model="tiiuae/falcon-7b-instruct",
#     trust_remote_code=True
# )

app = FastAPI()

# def call_ai_engine(prompt: str):
#     """
#     Call the AI engine with the provided prompt and return the response.
#     """
#     try:
#         response = model(
#             prompt,
#             max_new_tokens=150,
#             do_sample=True,
#             temperature=0.7,
#             top_p=0.9,
#             repetition_penalty=1.5,  # Stronger penalty
#             num_beams=4,             # Beam search helps quality
#             clean_up_tokenization_spaces=True
#         )
#         return response[0]['generated_text']
#     except Exception as e:
        # print(f"Error calling AI engine: {e}")
        # return "Error generating response from AI engine."

@app.post("/recommend")
async def recommend(request: Request):
    data = await request.json()

    url = "https://www.cse.lk/api/companyInfoSummery"

    response = requests.post(url, data={"symbol": "SAMP.N0000"})
    if response.status_code != 200:
        return {"error": "Failed to fetch company information"}
    company_info = response.json()

    companyMainData = {
        "currentPrice": company_info['reqSymbolInfo']['lastTradedPrice'],
        "high": company_info['reqSymbolInfo']['allHiPrice'],
        "low": company_info['reqSymbolInfo']['allLowPrice'],
        "change": company_info['reqSymbolInfo']['change'],
        "name": company_info['reqSymbolInfo']['name'],
        "volume": company_info['reqSymbolInfo']['tdyShareVolume'],
        "closingPrice": company_info['reqSymbolInfo']['closingPrice'],
    }

    # prompt = (
    #     "You are a financial advisor. Based on this company's current stock data, provide a short, realistic investment recommendation.\n\n"
    #     f"Company: {companyMainData['name']}\n"
    #     f"Current Price: {companyMainData['currentPrice']} LKR\n"
    #     f"Day High: {companyMainData['high']} LKR\n"
    #     f"Day Low: {companyMainData['low']} LKR\n"
    #     f"Change Today: {companyMainData['change']} LKR\n"
    #     f"Volume: {companyMainData['volume']}\n"
    #     f"Previous Close: {companyMainData['closingPrice']} LKR\n\n"
    #     "### Recommendation:"
    # )


    # modelResponse = call_ai_engine(prompt)
    # print("Model Response:", modelResponse)
    
    return {"recommendation": "demoo"}
