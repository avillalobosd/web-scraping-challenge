from splinter import Browser
from bs4 import BeautifulSoup
import re
import time
import requests
import datetime as dt
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)



@app.route("/")
def index():
    data = mongo.db.mars.find_one()
    print(data)
    title=f"<h1>{data['title']}</h1>"
    paragraph=f"<h2>{data['paragraph']}</h2></br>"
    image=data['image']
    imageHTML=f' <img src="{image}" alt="Image from NASA" width="500" height="600"> </br>'
    weather = f"<h2>Weather:</h2><h3>{data['weather']}</h3>"
    return(title+paragraph+imageHTML+weather)



@app.route("/scrape")
def scrape():
    db = mongo.db.mars

    info = {
    "title":"TITLE",
    "paragraph": "PARAGRAPH",
    "image": "IMAGE_URL",
    "weather": "TWEET-WEATHER",
    "last_modified": dt.datetime.now()
    }

    # SE EJECUTRA EL DRIVER DE CHROME SELENIUM
    executable_path = {'executable_path': 'D:\ChromeDriver/chromedriver'}
    brow = Browser('chrome', **executable_path)


    # ABRE LA PAGINA Y GUARDA SU HTML
    mars_url="https://mars.nasa.gov/news/"
    brow.visit(mars_url)
    time.sleep(2)
    mars_html=brow.html
    mars_news= BeautifulSoup(mars_html, 'html.parser')

    # # SE BUCA EL TITLE DEL ARTICULO
    title = mars_news.select_one('ul.item_list')
    news_title=title.find("div", class_='content_title').text
    info["title"]=news_title

    # # SACA Y ASIGNA EL VALOR DE PARRAFO
    content = mars_news.select_one('li.slide')
    news_p=content.find("div", class_='article_teaser_body').text
    info["paragraph"]=news_p


    # # # SACA Y ASIGNA EL VALOR DE LA URL DE LA IMAGEN
    jpl_url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    brow.visit(jpl_url)
    boton = brow.find_by_id('full_image')
    boton.click()
    time.sleep(2)
    moreInfo=brow.find_link_by_partial_text('more info')
    moreInfo.click()
    parse=brow.html
    parseSoup = BeautifulSoup(parse, 'html.parser')
    imagen=parseSoup.select_one('figure')
    imagen2=imagen.select_one('img')
    src=imagen2.get('src')
    featured_image_url = 'https://www.jpl.nasa.gov'+src
    info["image"]=featured_image_url


    # # SACA Y ASIGNA EL VALO DEL TWEET
    mars_tweet="https://twitter.com/marswxreport?lang=en"
    brow.visit(mars_tweet)
    time.sleep(3)
    mars_wtml=brow.html
    weatherS= BeautifulSoup(mars_wtml, 'html.parser')
    # mars_weather= weatherS.find_all('div', attrs={"data-testid":"tweet"})

    for el in weatherS.find_all('div', attrs={"data-testid":"tweet"}):
        if ("InSight" in el.get_text()):
            info["weather"]=el.get_text()
            print (el.get_text())
            break
        # print (el.get_text())

    print(info)
    db.replace_one({}, info, upsert=True)
    return "Se Extrajo la información correctamente"

# VARIABLE INICIAL






if __name__ == '__main__':
    app.run(debug=True, port=4000)
