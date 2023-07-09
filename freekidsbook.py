from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def index():
    return 'Hello, world!'

@app.route('/scrape')
def scrape_books():
    url = 'https://freekidsbooks.org/reading-level/children/'
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'html.parser')
    item = soup.find_all('div', class_='wrapper cleafix')

    for i in item:
        page_text = i.find_all('div', class_='post-nav')
        for p in page_text:
            last_page = p.find('li', class_='next')
            last_page_link = last_page.find('a').get('href')
            last_page_num = int(last_page_link[54:-1])

    urls = []
    for page in range(1, last_page_num + 1):
        link = f"https://freekidsbooks.org/reading-level/children/page/{page}/"
        page = requests.get(link).text
        doc = BeautifulSoup(page, "html.parser")
        urls.append(link)

    count = 1
    for u in urls:
        if count <=20:
            response = requests.get(u)
            soup = BeautifulSoup(response.text, 'html.parser')
            book = soup.find_all('div', class_='col-xs-12 col-sm-12 col-md-12 left-side')
            for b in book:
                image = b.find('img').get('data-src')
                title = b.find('h2').text
                author = b.find('p', class_='author').text
                desc = b.find('div', class_='book_description_middle')
                description = desc.find_all('p')[1].text
                genre = b.find('p', class_="age_group").find_all('a')
                genre_list = [c.text.strip() for c in genre]
                download = b.find('a', class_='download-book my-post-like').get('href')
                print('%s) Title: %s, Author: %s, Link: %s, Image: %s, Description: %s, Genre: %s' % (
                count, title, author, download, image, description, genre_list))
                count += 1
                id = db.collection('book(test)').document()
                data = {
                    'id': id.id,
                    'title': title,
                    'author': author,
                    'link': download,
                    'image': image,
                    'description': description,
                    'genres': genre_list
                }
                db.collection('book(test)').document(id.id).set(data)

        return 'Scraping completed!'

if __name__ == '__main__':
    app.run()
