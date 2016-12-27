import json
import threading
#from bs4 import BeautifulSoup
import re
import os
from urllib.request import urlopen,Request

import socket
socket.setdefaulttimeout(10)

#http://fm.baidu.com/dev/api/?tn=channellist
def get_channel_list(page_url):
    try:
        htmlDoc = urlopen(page_url).read().decode('utf8')
    except:
        return {}
    with open("./channle.json", mode = 'w', encoding = 'utf-8') as file:
        file.write(htmlDoc)

    file = open('channle.json')
    content = json.load(file)
    channel_list = content['channel_list']

    for channel in channel_list:
        print(channel['channel_name'])

    return channel_list

def get_song_list(channel_url):
    try:
        htmlDoc = urlopen(channel_url).read().decode('utf8')
    except:
        return{}
    
    with open("./songs.json", mode = 'w', encoding = 'utf-8') as file:
        file.write(htmlDoc)

    file = open('songs.json')
    content = json.load(file)
    song_id_list = content['list']

    #for song in song_id_list:
    #    print(song)
    return song_id_list

def get_song_real_url(song_url):
    try:
        htmlDoc = urlopen(song_url).read().decode('utf8')
        #print(htmlDoc)
    except:
        return(None, None, 0)

    with open("./song.json", mode = 'w', encoding = 'utf-8') as file:
        file.write(htmlDoc)

    file = open('song.json')
    content = json.load(file)
    #print(content['data']['songList'])
    try:
        song_link = content['data']['songList'][0]['songLink']
        song_name = content['data']['songList'][0]['songName']
        song_size = int(content['data']['songList'][0]['size'])
    except:
        print('get real link failed')
        return(None, None, 0)

    #print(song_name + ':' + song_link)
    return song_name, song_link, song_size



def donwn_mp3_by_link(song_link, song_name, song_size):
    file_name = song_name + ".mp3"
    base_dir = os.path.dirname(__file__)

    file_full_path = os.path.join(base_dir, file_name)
    if os.path.exists(file_full_path):
        return
    
    print("begin DownLoad %s, size = %d" % (song_name, song_size))
    mp3 = urlopen(song_link) 
    
    block_size = 8192
    down_loaded_size = 0
    
    file = open(file_full_path, "wb")
    while True:
        try:
            buffer = mp3.read(block_size)
            
            down_loaded_size += len(buffer)
      
            if(len(buffer) == 0):
                if down_loaded_size < song_size:
                    if os.path.exists(file_full_path):
                        os.remove(file_full_path)
                        print('download time out, file deleted')
                        with open('log.txt', 'a') as log_file:
                            log_file.write("time out rm %s\n" % file_name)
                break
            
            print('%s %d of %d' % (song_name, down_loaded_size, song_size))
            file.write(buffer)
            
            if down_loaded_size >= song_size:
                print('%s download finshed' % file_full_path)
                break

        except:
            if os.path.getsize(file_full_path) < song_size:
                if os.path.exists(file_full_path):
                    os.remove(file_full_path)
                    print('download time out, file deleted')
                    with open('log.txt', 'a') as log_file:
                        log_file.write("time out rm %s\n" % file_name)
            break

    file.close()
      

def downViaMutiThread(song_info_list):

    task_threads = []  #存储线程

    for song_name, song_link, song_size in song_info_list:
        t = threading.Thread(target = donwn_mp3_by_link, args = (song_link, song_name, song_size))
        task_threads.append(t)

    for task in task_threads:
        task.start()
    for task in task_threads:
        task.join()


if __name__ == '__main__':

    # 第一步，获取频道列表channel
    page_url = 'http://fm.baidu.com/dev/api/?tn=channellist'
    channel_list = get_channel_list(page_url)

    while True:
        #第二步，获取某个频道列表下的所有歌曲
        #get all song's id in one channel
        channel_url = 'http://fm.baidu.com/dev/api/?tn=playlist&format=json&id=%s' % 'public_yuzhong_yueyu'
        song_id_list = get_song_list(channel_url)

        #第三步，获取该歌曲的所有信息
        #get song real url
        #song_info = {}
        song_info_list = []
        for song_id in song_id_list:
            #print(song_id['id'])
            song_url = "http://music.baidu.com/data/music/fmlink?type=mp3&rate=320&songIds=%s" % song_id['id']
            song_name, song_link, song_size = get_song_real_url(song_url)
            if song_size != 0:
                #song_info[song_name] = song_link
                #song_info = (song_name, song_link, song_size)
                #song_info_list.append(song_info)

                #single thread way
                #最后下载歌曲
                donwn_mp3_by_link(song_link, song_name, song_size)

        #downViaMutiThread(song_info_list)

