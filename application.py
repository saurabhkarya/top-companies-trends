from flask import Flask, jsonify, render_template, request
import pandas as pd
from pytrends.request import TrendReq
from datetime import date
import time

application = Flask(__name__)

@application.route("/")
def home():
    return render_template('index.html')

@application.route("/trends", methods=['POST'])
def get_trends():
    # Instantiate pytrends
    pytrend = TrendReq(hl='en-US', tz=360)

    # Download the list of S&P500 companies
    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]

    # Get the company names
    company_names = df['Security'].tolist()[:5]

    # Create an empty DataFrame to store results
    results = pd.DataFrame(columns=['Company', str(date.today())])

    # For each company, perform Google Trends search
    for company in company_names:
        search_query = f"{company} share price"
        pytrend.build_payload(kw_list=[search_query])
        data = pytrend.interest_over_time()

        if not data.empty:
            mean_value = data[search_query].mean()
            new_row = pd.DataFrame([[company, mean_value]], columns=['Company', str(date.today())])
            results = pd.concat([results, new_row], ignore_index=True)

        # Sleep for 1 second to avoid hitting the rate limit
        time.sleep(1)

    # Sort by the search volume column
    results = results.sort_values(by=str(date.today()), ascending=False)

    # Return the results as JSON
    return jsonify(results.to_dict(orient='records'))

if __name__ == "__main__":
    app.run(debug=True)
