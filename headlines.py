# -*- coding: utf-8 -*-
"""
Headlines Project
@author: bilal
"""

from flask import Flask
from flask import render_template
from flask import request
import feedparser
import requests
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, LabelSet, HoverTool 
from bokeh.embed import components


API_KEY_OM = "7f9456d63fadcd1e8d9ef6372412f7a9"
#API_KEY_OM = "cb932829eacb6a0e9ee4f38bfbf112ed"
API_KEY_OPENEX = "9ebd0db7b139498ab4f653c4f7ddc8a7"


app = Flask(__name__)

RSS_FEEDS = {'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn':'http://rss.cnn.com/rss/edition.rss',
             'fox':'http://feeds.foxnews.com/foxnews/latest',
             'iol':'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'news': 'bbc',
            'city': 'lahore, pakistan',
            'currency_from':'usd',
            'currency_to':'pkr'}


@app.route("/")
def home():
    
    city = request.args.get("city")   
    if not city:
        city = DEFAULTS['city']    
    weather = get_weather(city)
    forcast = get_weather_forcast(city)
    plot = create_forcast_plot(forcast)
    
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from'] 
        
    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to =  DEFAULTS['currency_to']
        
    current_rate, currency_list = get_rate(currency_from,currency_to)
    current_rate = round(current_rate, 3)
     
    channel = request.args.get("channel")
    if not channel or channel.lower() not in RSS_FEEDS:
        
        channel = DEFAULTS['news']
    feeds = get_news(channel.lower())
    
    script, div = components(plot)
    
    return render_template("home.html",
                           channel = channel.upper(),
                           articles = feeds,
                           currency_from = currency_from.upper(),
                           currency_to = currency_to.upper(),
                           current_rate = current_rate,
                           currency_list = sorted(currency_list),
                           weather = weather,
                           script=script,
                           div=div)

def get_news(channel):
    """Retrive Feeds from the chosen list of news channels"""
    
    channel = channel.lower()
    rss_feed = feedparser.parse(RSS_FEEDS.get(channel))    
    feeds = rss_feed['entries']
    return feeds
    
    

def get_weather(city):
    """Get weather information for a given city"""
    
    url = "http://api.openweathermap.org/data/2.5/weather"
    
    response = requests.get(url, params = {"q":city,
                                           "units":"metric",
                                           "appid":API_KEY_OM})
    
    if response.status_code == 200:    
        data = response.json()
        weather = {"description":data["weather"][0]["description"],
                    "temperature":data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "city":data["name"],
                    'country': data['sys']['country']}
        return weather

    else:
        return None
    
        

def get_weather_forcast(city_name):
    """Get the weather forecasts for the city provided"""
    units = "metric"
    url = "http://api.openweathermap.org/data/2.5/forecast"

    response = requests.get(url,params={"q": city_name,"units":units,"appid":API_KEY_OM})
    data = response.json()
    city = {"name": data['city']['name'], "country" : data['city']['country']}
    
    forecast = []
    for datapoint in data['list']:
        info = {"wind": datapoint['wind']['speed'],
                "dt": pd.to_datetime(datapoint['dt_txt']),
                "cloud":datapoint['clouds']['all'],
                "description": datapoint['weather'][0]['description'],
                "temperature":datapoint['main']['temp'],
                "humidity": datapoint['main']['humidity'],
                "pressure": datapoint['main']['pressure']
            }
        
        forecast.append(info)
        
           
    return {"city": city, "forecast": forecast}



def get_rate(fr,to):
    """Get currency rate from to to currency using UDS as a common currency"""
    
    CURRENCY_URL = "https://openexchangerates.org//api/latest.json"
    response = requests.get(CURRENCY_URL, params = {"app_id":API_KEY_OPENEX})
    currency_list = response.json()['rates'].keys()
    rate = response.json()['rates'][to.upper()]/ response.json()['rates'][fr.upper()]
    return rate, currency_list  


def create_forcast_plot(forecast_data):
    """Creates Bokeh plot"""
    
    df = pd.DataFrame(forecast_data["forecast"])
    df.set_index("dt",inplace = True)
    df.sort_index(inplace=True)
    source = ColumnDataSource(df)
        
    TITLE = "Forecasts of Weather conditions in {}, {}".format(forecast_data["city"]["name"],forecast_data["city"]["country"])
    
    tools = []
    hover = HoverTool(tooltips=[
        ("temperature:", "@{temperature}&#8451"),
        ("humidity", "@{humidity}%"),
        ("windspeed", "@{wind}m/s"),
        ("cloudiness", "@{cloud}%"),
        ("weather","@description")
    ])
        
    tools.append(hover)
    
    p = figure(tools=tools, toolbar_location="above", logo="grey",
               x_axis_type="datetime", plot_width = 1000, plot_height = 350,  title=TITLE)
    
    p.xaxis.axis_label = "Day"
    p.yaxis.axis_label = "Temperature/C"
    
    
    p.line('dt', 'temperature', source=source,color = 'navy')
    
    p.scatter('dt', 'temperature', source=source, color='navy')
    labels = LabelSet(x= "dt", y= "temperature", text="description", y_offset=14,
                      text_font_size="8pt", text_color="#555555",
                      source=source, text_align='center')
    p.add_layout(labels)
    
    return p




if __name__ == "__main__":
    app.run(host = '0.0.0.0',
            port = 5001, debug = True)
    