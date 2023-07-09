from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import schedule
import time

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def delete_all_documents(collection_name):
    # Get all documents in the collection
    docs = db.collection(collection_name).stream()
    count = 0

    for doc in docs:
        doc_ref = db.collection(collection_name).document(doc.id)
        doc_data = doc_ref.get()

        if doc_data.exists:
            doc_ref.delete()
            count += 1

    print("Deleted", count, "documents in collection:", collection_name)

def scrape_data():

    delete_all_documents('eBook')

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
        page = requests.get(url).text
        doc = BeautifulSoup(page, "html.parser")
        urls.append(link)

    count = 1
    for u in urls:
        print(u)
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
            download = b.find('a', class_='download-book my-post-like')
            print('%s) Title: %s , Author: %s, Link: %s, Image: %s, Description: %s, Genre: %s' % (
            count, title, author, download, image, description, genre_list))
            count = count + 1
            id = db.collection('eBook').document()
            data = {
                'id': id.id,
                'title': title,
                'author': author,
                'link': download,
                'image': image,
                'description': description,
                'genres': genre_list
            }
            db.collection('eBook').document(id.id).set(data)

# Schedule the scraping task to run at 12 AM every day
schedule.every().day.at("19:20").do(scrape_data)

# Run the scheduler indefinitely
while True:
    schedule.run_pending()
    time.sleep(1)
