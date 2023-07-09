from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

url = f'https://freekidsbooks.org/'
r = requests.get(url).text
soup = BeautifulSoup(r, 'html.parser')
item = soup.find_all('div', class_='wrapper cleafix')

cate_urls = []
last_page_urls = []
page_dict = {}
urls = []
cate_names = []
category_genre = {}

for i in item:
    cate = i.find_all('ul', class_='dcw')
    for c in cate:
        all_cate = c.find_all('li')
        for a in all_cate:
            cate_link = a.find('a')
            category_link = cate_link.get('href')
            category_name = cate_link.text
            cate_urls.append(category_link)
            cate_names.append(category_name)
            id = db.collection('category').document()
            data = {
                'id': id.id,
                'genre': category_name
            }
            db.collection('category').document(id.id).set(data)

# for c in cate_urls:
#     response = requests.get(c)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     page_text = soup.find_all('div', class_='post-nav')

#     if page_text:
#         for p in page_text:
#             last_page_text = p.find('li', class_='next')
#             last_page_link = last_page_text.find('a').get('href')
#             last_page_urls.append(last_page_link)
#     else:
#         last_page_link = c+'page/1/'
#         last_page_urls.append(last_page_link)

# for cate_url, last_page_url in zip(cate_urls, last_page_urls):
#     response = requests.get(last_page_url)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     page_text = soup.find_all('div', class_='post-nav')
    
#     if page_text:
#         for p in page_text:
#             active_page = p.find('span', class_='active')
#             if active_page:
#                 last_page = int(active_page.text)
#             else:
#                 last_page = 1
#             page_dict[cate_url] = last_page
#     else:
#         page_dict[cate_url] = 1


# for cate_urls, page in page_dict.items():
#     for p in range(1, page + 1):
#         link = cate_urls + f"page/{p}/"
#         urls.append(link)

# count = 1
# for u in urls:
#     print(u)
#     response = requests.get(u)
#     soup = BeautifulSoup(response.text, 'html.parser')
#     book = soup.find_all('div', class_ = 'col-xs-12 col-sm-12 col-md-12 left-side')
#     for b in book:
#         base_url = u.split('/page/')[0]  # Extract the base URL
#         genre = base_url[34:]
#         image = b.find('img').get('data-src')
#         title = b.find('h2').text
#         author = b.find('p', class_ = 'author').text
#         desc = b.find('div', class_ = 'book_description_middle')
#         description = desc.find_all('p')[1].text        
#         download_link = b.find('a', class_ = 'download-book my-post-like')
#         if download_link:
#             download = download_link.get('href')
#             print('%s) Title: %s , Author: %s, Link: %s, Image: %s, Description: %s, Genre: %s' % (
#                 count, title, author, download, image, description, genre))
#             count = count + 1
#             id = db.collection('eBook').document()
#             data = {
#                 'id': id.id,
#                 'title': title,
#                 'author': author,
#                 'link': download,
#                 'image': image,
#                 'description': description,
#                 'genres': genre
#             }
#             db.collection('eBook').document(id.id).set(data)
#         else:
#             print('%s) Title: %s , Author: %s - No download link available' % (count, title, author))
#             count = count + 1