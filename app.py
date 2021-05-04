from flask import Flask, render_template, request, redirect
import requests
import json
from dotenv import dotenv_values
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.embed import components, server_document, file_html, json_item
from bokeh.models import HoverTool
from bokeh.resources import CDN
#from jinja import Template
import os
#import alpha_vantage# import make_graph

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        #print(result)
        #plot = make_graph(ticker_name, type_of_graph)
        #script, div = components(plot)
        ticker = request.form.get("ticker")
        key = os.environ['VANTAGEAPI']
        type_of_graph = request.form.get("features")
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}'.format(ticker, key)
        response = requests.get(url)

        df_API = pd.DataFrame.from_dict(
            response.json()['Time Series (Daily)'], 
            orient='index'
        )

        df_API.columns=['open', 'high', 'low', 'close', 'adjusted close', 'volume', 'dividend amount', 'split coefficient']      

        df_API.index = pd.to_datetime(df_API.index, format='%Y/%m/%d')
        df_API[type_of_graph] = pd.to_numeric(df_API[type_of_graph])

        x = df_API.index.tolist()
        y = df_API[type_of_graph].tolist()

        p = figure(
            title="Stock Price at " + type_of_graph, 
            x_axis_label='Month and Year', 
            y_axis_label='Stock Price in USD', 
            x_axis_type='datetime'
        )
        p.line(x, y, line_width=2)
        p.add_tools(HoverTool())
        script, div = components(p)
        #item_text = json.dumps(json_item(p, "myplot"))
        #item = JSON.parse(item_text);
        #Bokeh.embed.embed_item(item);
        return render_template("result.html",result = result, the_div=div, the_script=script)

if __name__ == '__main__':
    app.run(port=33507)