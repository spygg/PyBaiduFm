import requests
import threading
from bs4 import BeautifulSoup
import re
import os
from urllib.request import urlopen,Request

def download_pic_by_link(pic_link, abulm_name):
    if os.path.exists('./%s' % abulm_name):
        pass
    else:
        try:
            os.makedirs('./%s' % abulm_name)
        except:
            pass

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = Request(url=pic_link, headers=headers)
    try:
        img = urlopen(req).read()
    except :
        return

    pic_name =  pic_link.replace("/","-")
    if 'com-' in pic_name:
        p = re.compile(r'com-')
        pic_name = p.split(pic_name)[1]

    with open('./%s/%s' % (abulm_name, pic_name), 'wb') as file:
        file.write(img)

def get_pic_links(topic_url):
    pic_links = []
    htmlDoc = urlopen(topic_url).read()
    soup = BeautifulSoup(htmlDoc, 'html.parser')
    links = soup.find_all('img', id = re.compile(r'aimg'))

    for link in links:
        pic_links.append(link['src'])

    return pic_links

def get_topic_infos(page_url):
    topic_info = {}
    htmlDoc = urlopen(page_url).read()
    soup = BeautifulSoup(htmlDoc, 'html.parser', from_encoding='utf-8')


    i = 1
    for top_links in soup.find_all('th', class_ = re.compile(r'new')):
        links = top_links.find('a', href = re.compile(r'thread'))

        link = r'http://sex8.cc/' + links['href']
        abulm_name = links.get_text()

        print('the %d topic ' % i + link)
        print(abulm_name)

        topic_info[link] = abulm_name
        i = i + 1


    return topic_info



def get_page_links(forum_link):
    page_links = []
    htmlDoc = urlopen(forum_link).read()
    soup = BeautifulSoup(htmlDoc, 'html.parser')
    links = soup.find('a', totalpage = re.compile(r'\d+'))

    total_num = int(links['totalpage']) + 1
    #print(links['totalpage'])
    print("共有 %s 页" % links['totalpage'])

    for i in range(1, total_num):
        link = 'http://sex8.cc/forum-158-%d.html' % i
        page_links.append(link)

    return page_links


def downImageViaMutiThread(pic_links, ablum_name):
    task_threads = []  #存储线程

    for pic_link in pic_links:
        t = threading.Thread(target = download_pic_by_link, args = (pic_link, ablum_name))
        task_threads.append(t)

    for task in task_threads:
        task.start()
    for task in task_threads:
        task.join()


if __name__ == '__main__':
    forum_link = r'http://sex8.cc/forum-158-1.html'
    page_links = get_page_links(forum_link)

    for page_link in page_links:
        topic_infos = get_topic_infos(page_link)

        for topic_link, ablum_name in topic_infos.items():
            pic_links = get_pic_links(topic_link)
            downImageViaMutiThread(pic_links, ablum_name)
            #for pic_link in pic_links:
            #    download_pic_by_link(pic_link, ablum_name)

