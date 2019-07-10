import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from .models import NewsInfo
from .serializers import NewsInfoSerializer
from rest_framework import viewsets
# Create your views here.


def get_news_links():
    url = "https://nba.udn.com/nba/index?gr=www"
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.find_all('a')  # find hot news links
    news_links = []
    for link in links:
        href = link.get('href')

        if href is not None and href.startswith("/nba/story/6780/"):
            news_links.append("https://nba.udn.com/" + href)
    return news_links


def get_news_info(news_url):
    title = []
    date = []
    image = []
    article = []
    for n in news_url:
        resp = requests.get(n)
        resp.encoding = 'utf-8'
        sp = BeautifulSoup(resp.text, 'html.parser')
        img = sp.find_all('img', {'data-sizes': "auto"})  # find  news image
        for i in img:
            image.append(i.get('data-src'))
        title.append(sp.h1.text)  # find hot news title
        time = sp.find_all('div', 'shareBar__info--author')  # datetime for news
        for t in time:
            date.append(t.span.text)
        content = sp.find_all('p')  # find hot news article
        ar = []
        a = ''
        for c in content:
            ar.append(c.text.replace(" ", "").replace("'", "`"))
        del ar[0]
        # print(ar)
        a = a.join(ar)  # 合併多個字串為一個字串
        article.append(a)
    return title, date, image, article


'''crawler data and save'''
news_url = get_news_links()
[title, date, image, article] = get_news_info(news_url)
NewsInfo.objects.all().delete()
for i in range(len(title)):
    NewsInfo.objects.create(title=title[i], datetime=date[i], image=image[i], content=article[i])


def news_index(request, id):
    p = NewsInfo.objects.get(id=id)
    return render(request, 'article.html', locals())


def homepage(request):
    news = NewsInfo.objects.all()
    return render(request, 'homepage.html', locals())


class MainSiteViewSet(viewsets.ModelViewSet):
    queryset = NewsInfo.objects.all()
    serializer_class = NewsInfoSerializer
