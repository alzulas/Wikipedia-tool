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
                                allLinks.append('https://en.wikipedia.org' + link.attrs['href'])
    del allLinks[0]
    allLinks = allLinks[:-26]
    return(allLinks)

def grab_all_history(url, topic, df_all_history):
    dif_url = None
    page_no = 1
    yesterday = datetime.now() - timedelta(days = 2)
    latest_date = datetime.now()
    while latest_date > yesterday:
        html = urlopen(url)
        bs = BeautifulSoup(html, 'html.parser')
        for li_tag in bs.find_all('li'):
            tags = []
            has_no_comment = True
            first_tag_comment = True
            line_for_append = [url, topic]
            if 'data-mw-revid' in li_tag.attrs:
                for a_tag in li_tag.find_all('a'):
                    if str(a_tag).__contains__('prev') and str(a_tag).__contains__('diff'):
                        dif_url = 'https://en.wikipedia.org' + str(a_tag.attrs['href'])
                        final_marker = ['','']
                    if str(a_tag).__contains__('mw-changeslist-date'):
                        line_for_append.append(a_tag.text)
                        latest_date = datetime.strptime(a_tag.text, '%H:%M, %d %B %Y')
                        if latest_date < yesterday:
                            return(df_all_history)
                    if str(a_tag).__contains__('mw-userlink'):
                        line_for_append.append(a_tag.text)
                for span_tag in li_tag.find_all('span'):
                    if str(span_tag).__contains__('data-mw-bytes'):
                        line_for_append.append(span_tag.text)
                    if str(span_tag).__contains__('mw-plusminus'):
                        line_for_append.append(span_tag.text)
                    if str(span_tag).__contains__('comment') and has_no_comment:
                        line_for_append.append(span_tag.text)
                        has_no_comment = False
                    if str(span_tag).__contains__('mw-tag-marker'):
                        if first_tag_comment:
                            first_tag_comment = False
                        else:
                            splits = re.split('>', str(span_tag))
                            if str(span_tag).__contains__('href'):
                                tags.append(splits[-3][:-3])
                            else:
                                tags.append(splits[-2][:-6])
                if has_no_comment:
                    line_for_append.append("No comment")
            line_for_append.append(tags)
            if dif_url:
                line_for_append.append(dif_url)
            try:
                df_all_history.loc[len(df_all_history)] = line_for_append
            except:
                continue
        url = ''
        for a_tag in bs.find_all('a'):
            if str(a_tag).__contains__('mw-nextlink'):
                url = 'https://en.wikipedia.org' + str(a_tag.attrs['href'])
    return(df_all_history)

@app.route('/')
def index():
    allLinks = get_links()
    df_all_history = pd.DataFrame(columns=['Page', 'Topic', 'Date of Change', 'User', 'Bytes', 'Number of Changes', 'Comments', 'Tags', 'Link To Diff'])
    for topic in tqdm(allLinks[:20]):
        url = 'https://en.wikipedia.org/w/index.php?title=:' + topic[6:] + '&action=history'
        topic = topic[6:]
        df_all_history = pd.concat([df_all_history, grab_all_history(url, topic, df_all_history)])
        shape_of_data = df_all_history.shape
        if shape_of_data[0] > 20:
            history_list = [df_all_history.columns.values.tolist()] + df_all_history.values.tolist()
            return render_template('index.html', table_list=allLinks)
    return render_template('index.html', table_list=allLinks)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    return render_template("result.html")

if __name__ == '__main__':
    app.run(port=33507)