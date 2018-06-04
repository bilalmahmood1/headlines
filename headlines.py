# -*- coding: utf-8 -*-
"""
Headlines Project
@author: bilal
"""

from flask import Flask
from flask import render_template
import feedparser


app = Flask(__name__)

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn':'http://rss.cnn.com/rss/edition.rss',
             'fox':'http://feeds.foxnews.com/foxnews/latest',
             'iol':'http://www.iol.co.za/cmlink/1.640'}

@app.route("/")
@app.route("/<channel>")
def route(channel = 'bbc'):
    return get_news(channel)

def get_news(channel):
    rss_feed = feedparser.parse(RSS_FEEDS.get(channel))
    if rss_feed['bozo'] == 1:
        return render_template("error.html",
                               channel = channel.upper(),
                               channels = RSS_FEEDS.keys())
    else:    
        feeds = rss_feed['entries']
        return render_template("home.html",
                               channel = channel.upper(),
                               articles = feeds)
            
        
if __name__ == "__main__":
    app.run(host = '0.0.0.0',
            port = 5000, debug = True)
    