RUN install lib:

pip install requests
pip install pandas

RUN file
python your_path\detect_lang.py

Input file name or Index from for next time (Default auto run with max index in Output files)
Schema file must same as Image.csv
If want re-run ALL -> delete file output
Note: 
Status=200 it's OK, status=invalid -> url image invalid, other: limit of api or authen error
With Status=200 text = "" is no text in image, text != "" -> Text in Image. You can filter with condition
I created 15 token for you with 25k/request per month, and limit size 1M for image