from django.shortcuts import render,redirect
from django.http import HttpResponse
from datetime import datetime
from .models import *
import nltk
from newspaper import Article
import requests
import time
from bs4 import BeautifulSoup
from page.models import Contact

class Artic:
    def __init__(self,text,title,author):
        self.text=text
        self.title=title
        self.author=author
    
    def out(self):
        return (self.title+"</p></p>"+self.author+"</p></p>"+self.text+"</p></p>")

z=""
def web_scrape(query, num = 10, doc_start = 1, start_query = 1, end_query = -1):
    if end_query == -1:
        end_query = num
    assert isinstance(query, str) and isinstance(num, int) and isinstance(start_query, int) and isinstance(end_query, int)
    assert num >= 1 and start_query <= end_query and start_query > 0 and end_query <= num
    start_query -= 1
    query+='_editorial'
    search_url = 'https://www.google.com/search?q={}&num={}&lr=lang_en&ie=UTF-8'.format(query, num + 10)
    res = requests.get(search_url)

    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all('a')

    all_links = []
    for item in text:
          all_links.append(item.get('href'))

    links = []
    for item in all_links:
        if(item.startswith('/url?q=')):
            links.append(item)
           
    assert len(links) >= num
    output=''
    j=0
    lis=[]
    for i in range(start_query, end_query):
        url = 'https://www.google.com/' + links[i]
        article = Article(url)
        article.download()
        article.parse()
        nltk.download('punkt')
        article.nlp()
        text = article.text
        author = []
        keyword = []
        
        if len(text) > 300:
            j=j+1
            author = article.authors
            title = article.title
            keyword = article.keywords
            au=""
            if len(author) > 0:
                for a in author:
                    au+=a+" , "
            key=""
            for k in keyword:
                key+=k+" , "
            tex=""
            for t in text:
                tex += t
            lin=""
            lin+=str(links[i])
            a1=Artic(tex,title,au)
            #a1.out()
            lis.append(a1)
            output+=a1.out()
            output += "</p></p>"
            output+= "----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"+"\n"
            output += "</p></p>"
            
    

            

    #fname = query + ".txt"

    fname = "saved_editorial.txt"
    z=fname
    import io
    with io.open(fname, "w", encoding="utf-8") as f:
        f.write(output)
        f.close
        time.sleep(1)
        doc_start = doc_start+1
    return lis

def search(request):
    if 'query' in request.GET:
        query = request.GET.get('query', '')
        return render(request,'result.html',{'article':web_scrape(query)})
    return render(request,'search.html')

def contact(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        desc=request.POST.get('desc')
        x=Contact(name=name,email=email,desc=desc,date=datetime.today())
        x.save()
       
    return render(request,'contact.html')

def about(request):
    return render(request,'about.html')


from httplib2 import Http
import google.oauth2.credentials
import google_auth_oauthlib.flow


def save(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive'])
    flow.redirect_uri = 'http://127.0.0.1:8000/upload'
    authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
    return redirect(authorization_url)

from googleapiclient.discovery import build
from apiclient.http import MediaFileUpload

def upload(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/drive'])
    flow.redirect_uri = 'http://127.0.0.1:8000/upload'
    authorization_response =request.build_absolute_uri()
    if "http:" in authorization_response:
        authorization_response = "https:" + authorization_response[5:]
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes}

    drive_service = build('drive', 'v3', credentials=credentials)
    file_metadata = {
    'name': 'saved_editorial.txt',                                                                     # name change acc to file 
    'mimeType': '*/*'
    }
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    media = MediaFileUpload(os.path.join(BASE_DIR, 'saved_editorial.txt'),                              # correct file upload
                            mimetype='*/*',
                            resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print ('File ID: ' + file.get('id'))

    return render(request,'upload.html')
