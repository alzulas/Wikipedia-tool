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
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns 
from tqdm import tqdm

app = Flask(__name__)


def get_links():
    html = urlopen('https://en.wikipedia.org/wiki/Wikipedia:List_of_controversial_issues')
    bs = BeautifulSoup(html, 'html.parser')
    allLinks = []
    various_not_allowed = ['Wikipedia', '%', 'http', 'www']
    for link in bs.find_all('a'):
        if 'href' in link.attrs:
            if 'wiki' in link.attrs['href']:
                if various_not_allowed[0] not in link.attrs['href']:
                    if various_not_allowed[1] not in link.attrs['href']:
                        if various_not_allowed[2] not in link.attrs['href']:
                            if various_not_allowed[3] not in link.attrs['href']:
                                allLinks.append(link.attrs['href'])
    del allLinks[0]
    allLinks = allLinks[:-26]
    #print(allLinks)
    return(allLinks)

@app.route('/')
def index():
    links = get_links()
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    return render_template("result.html")

if __name__ == '__main__':
    app.run(port=33507)