from flask import Flask, render_template, request, redirect
import requests
import json
from dotenv import dotenv_values
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.embed import components, server_document, file_html, json_item
from bokeh.models import HoverTool
from bokeh.resources import CDN
import os
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import seaborn as sns 

app = Flask(__name__)

@app.route('/')
def index():
    df_all_history = pd.DataFrame(columns=['Page', 'Topic', 'Date of Change', 'User', 'Bytes', 'Number of Changes', 'Comments', 'Tags', 'Link To Diff'])
    df_all_history = pd.read_csv('todays_entries.csv')
    history_list = [df_all_history.columns.values.tolist()] + df_all_history.values.tolist()
    return render_template('index.html', table_list=history_list)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    return render_template("result.html")

if __name__ == '__main__':
    app.run(port=33507)