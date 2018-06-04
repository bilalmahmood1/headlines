#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Headlines Project
@author: bilal
"""

from flask import Flask
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
    ## A really simple way to handle internet breakdown or wrong URLS
    if len(rss_feed.entries) == 0 or rss_feed.status != 200:
        return """<html>
                     <body>
                     <h1>Can't Access Feeds Right Now!</h1>
                    </body>
                  </html>"""
    else:              
        entry_html_block = """
             <b>{0}</b><br/> 
             <i>{1}</i><br/>
             <p>{2}</p><br/>        
        """
        content = ""  
        for entry in rss_feed['entries']:
            content += entry_html_block.format(entry.get('title'),
                                entry.get('published'),
                                entry.get('summary'))
        
        html_page = """<html>
                         <body>
                         <h1>{0} Headlines </h1>
                         {1}
                        </body>
                      </html>"""
                      
        return html_page.format(channel.upper(), content)
        

if __name__ == "__main__":
    app.run(host = 'localhost',
            port = 5000, debug = True)
    