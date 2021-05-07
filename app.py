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
    #print(allLinks)
    return(allLinks)

def grab_all_history(url, topic, df_all_history):
    print(url)
    dif_url = None
    link_still_there = True
    page_no = 1
    yesterday = datetime.now() - timedelta(days = 2)
    latest_date = datetime.now()
    # While statement loops through all pages of the change history
    while latest_date > yesterday:
        print("while start")
        now = datetime.now()
        print("Starting page " + str(page_no) + " at " + now.strftime("%m/%d/%Y, %H:%M:%S"))
        html = urlopen(url)
        bs = BeautifulSoup(html, 'html.parser')
        # Changes are in <li>, but not all li
        for li_tag in bs.find_all('li'):
            tags = []
            has_no_comment = True
            first_tag_comment = True
            line_for_append = [url, topic]
            # data-mw-revid begins the insert for each change
            if 'data-mw-revid' in li_tag.attrs:
                # dates and user names exist inside of <a> tags
                for a_tag in li_tag.find_all('a'):
                    if str(a_tag).__contains__('prev') and str(a_tag).__contains__('diff'):
                        dif_url = 'https://en.wikipedia.org' + str(a_tag.attrs['href'])
                        final_marker = ['','']
                    # Date
                    if str(a_tag).__contains__('mw-changeslist-date'):
                        line_for_append.append(a_tag.text)
                        latest_date = datetime.strptime(a_tag.text, '%H:%M, %d %B %Y')
                        if latest_date < yesterday:
                            break
                    # User
                    if str(a_tag).__contains__('mw-userlink'):
                        line_for_append.append(a_tag.text)
                # All other data exists inside of <span> tags
                for span_tag in li_tag.find_all('span'):
                    # Bytes
                    if str(span_tag).__contains__('data-mw-bytes'):
                        line_for_append.append(span_tag.text)
                    # Number of changes
                    if str(span_tag).__contains__('mw-plusminus'):
                        line_for_append.append(span_tag.text)
                    # Comments
                    if str(span_tag).__contains__('comment') and has_no_comment:
                        line_for_append.append(span_tag.text)
                        has_no_comment = False
                    # Tags
                    if str(span_tag).__contains__('mw-tag-marker'):
                        if first_tag_comment:
                            first_tag_comment = False
                        else:
                            splits = re.split('>', str(span_tag))
                            if str(span_tag).__contains__('href'):
                                tags.append(splits[-3][:-3])
                            else:
                                tags.append(splits[-2][:-6])
                # In the case that there are no comments
                if has_no_comment:
                    line_for_append.append("No comment")
            line_for_append.append(tags)
            if dif_url:
                line_for_append.append(dif_url)
            # add line to dataframe
            try:
                df_all_history.loc[len(df_all_history)] = line_for_append
            except:
                continue
        url = ''
        # Get next page of history
        for a_tag in bs.find_all('a'):
            if str(a_tag).__contains__('mw-nextlink'):
                url = 'https://en.wikipedia.org' + str(a_tag.attrs['href'])
        # If no next page, break while loop
        link_still_there = False
    return(df_all_history)

@app.route('/')
def index():
    allLinks = get_links()
    df_all_history = pd.DataFrame(columns=['Page', 'Topic', 'Date of Change', 'User', 'Bytes', 'Number of Changes', 'Comments', 'Tags', 'Link To Diff'])
    for topic in tqdm(allLinks):
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