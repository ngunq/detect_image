import pandas as pd
import requests
import os
from files import keys
import time
import csv

def create_index_csv(file_name):
    df = pd.read_csv(f"./files/{file_name}.csv")
    df.insert(0, "Numbers", range(1, len(df) + 1))
    # Create index use it same as unique id

    df.to_csv(f"./files/{file_name}Index.csv", index=False)
    print("Done create index.")

def get_valid_token():
    for token in keys.tokens:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            data={
                'apikey': token, 
                'language': 'auto', 
                'OCREngine': 2,
                'url': 'https://cdn.shopify.com/s/files/1/0729/7934/9806/files/20241018-ace8b7a958bf8ea4-w800h800.png?v=1746317903'
            }
        )
        if response.status_code == 200:
            return token

    return None

def contains_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return "True"
    return "False"
        
def detect_text(image_url, API_KEY):
    print('Processing:', image_url)
    response = requests.post(
            'https://api.ocr.space/parse/image',
            data={'apikey': API_KEY, 
                'language': 'auto', 
                'OCREngine': 2,
                'url': image_url},
            timeout=5
        )
    if response.status_code == 200:
        try:
            result = response.json()
            text = result['ParsedResults'][0]['ParsedText']
            status = '200'
        except:
            text = str(response.json())
            status = 'invalid'
    else:
        text = str(response.json())
        status = str(response.status_code)

    return status, text

def main_flow(file_name, from_index: int = None):
    API_KEY  = get_valid_token()
    print("Using token:", API_KEY)
    if API_KEY:
        try:
            dft = pd.read_csv(f"./files/{file_name}Output.csv",  sep='|', quoting=csv.QUOTE_ALL, escapechar='\\')
            max_index = dft["Numbers"].max()
            print('Max index:', max_index)
        except:
            max_index = 0
        
        if from_index:
            max_index = from_index
        df = pd.read_csv(f"./files/{file_name}Index.csv")
        # Read next index
        if int(max_index) >= 5:
            df_filtered = df[df["Numbers"] > int(max_index) - 5].copy()
        else:
            df_filtered = df[df["Numbers"] > 0].copy()

        output_file = f"./files/{file_name}Output.csv"

        # Write header Output
        if not os.path.exists(output_file):
            df_filtered["status"] = ""
            df_filtered["text"] = ""
            df_filtered["is_chinese"] = "False"
            df_filtered.head(0).to_csv(output_file, index=False,  sep='|', quoting=csv.QUOTE_ALL, escapechar='\\')

        for i, row in df_filtered.iterrows():
            img = row["Image Src"]
            try:
                if img.find('https://') != -1:
                    status, text = detect_text(img, API_KEY)
                    is_chinese = contains_chinese(text)
                else:
                    status, text = "", ""
                    is_chinese = "False"
            except:
                status, text = "", ""
                is_chinese = "False"

            df_filtered.at[i, "status"] = status
            df_filtered.at[i, "text"] = text
            df_filtered.at[i, "is_chinese"] = is_chinese
            df_filtered.loc[[i]].reset_index(drop=True).to_csv(output_file, mode='a', header=False, index=False, sep='|', quoting=csv.QUOTE_ALL, escapechar='\\')
            time.sleep(0.5)
    else:
        print("Please create new API Key.")

# # First time create index
# create_index_csv(file_name='Image')

main_flow(file_name= 'Image')


# Input file name or Index from for next time (Default auto run with max index in Output files)
# Schema file must same as Image.csv
# If want re-run ALL -> delete file output
# Note: 
# Status=200 it's OK, status=invalid -> url image invalid, other: limit of api or authen error
# With Status=200 text = "" is no text in image, text != "" -> Text in Image. You can filter with condition
# I created 15 token for you with 25k/request per month, and limit size 1M for image
