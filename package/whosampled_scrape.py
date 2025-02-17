# import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()


def retrieve_song_link(song_name, artist_name=None):

    query = song_name.split('(')[0].replace(' ', '%20').replace("'", '%27') +'%20'+ artist_name.replace(' ', '%20')
    url = 'https://www.whosampled.com/search/tracks/?q={}'.format(query)
    # print(url)
    r = http.request('GET', url)
    content = r.data
    soup = BeautifulSoup(content, 'html.parser')
    stuff = soup.findAll('li', attrs={'class': "listEntry"})
    stuff2 = soup.findAll('span', attrs={'class': "trackArtist"})
    if stuff:
        link = [i.a for i in stuff][0].get('href')
        # print([i.a for i in stuff2][0].get('href'),artist_name)
        return link
    # else:
#         print('{} not found on whosampled'.format(song_name))

def retrieve_samples_v2(song_name, link):
    samples = []
    sampled_by = []
    s = http.request('GET', 'https://www.whosampled.com'+link)
    content1 = s.data
    soup = BeautifulSoup(content1, 'html.parser')
    listed = [i.text for i in soup.findAll('div', attrs={'class':'list bordered-list'})]
    if len(listed) == 2:
        there_in = [i.split('\n') for i in list(filter(None, listed[0].split('\t')))][:-1]
        there_out = [i.split('\n') for i in list(filter(None, listed[1].split('\t')))][:-1]
        for j in there_out:
            # print('there_out', song_name, j, len(j))
            sampled_by.append({'query':song_name, 'type':j[-7], 'genre':j[-6], 'title':j[-3], 'artist':j[-2].replace('by ', '').split(' (')[0], 'year': j[-2].replace('by ', '').split(' (')[1].replace(')', '')})
    else:
        there_in = [i.split('\n') for i in list(filter(None, listed[0].split('\t')))][:-1]

    for i in there_in:
        # print('there_in', song_name, i, len(i))
        try:
            samples.append({'query':song_name, 'type':i[-7], 'genre':i[-6], 'title':i[-3], 'artist':i[-2].replace('by ', '').split(' (')[0], 'year': i[-2].replace('by ', '').split(' (')[1].replace(')', '')})
        except IndexError as e:
            print(e)
    return samples, sampled_by

def getme_thesamples(song_name, artist_name):
    link = retrieve_song_link(song_name, artist_name)
    if link:
        samples, sampled_by = retrieve_samples_v2(song_name, link)
        return samples, sampled_by
    else:
        return None, None

def get_whosampled_playlist(loaded_playlist):
    # samples = []
    sb_data = []
    new_playlist = []
    print('SPOTIFY PLAYLIST DISCOVERED: \n')
    for i in loaded_playlist:
        print(i['track']+' by '+i['artist'][0])
    for i in loaded_playlist:
        samples, sampled_by = getme_thesamples(i['track'], i['artist'][0])
        if samples:
            new_playlist.append(samples)
        if sampled_by:
            sb_data.append(sampled_by)

    lst = [i for j in new_playlist for i in j]
    sb_data = [i for j in sb_data for i in j]
    sample_data = pd.DataFrame(lst)
    sample_data.to_csv('samples.csv')
    sb_data = pd.DataFrame(sb_data)
    sb_data.to_csv('sampled_by.csv')
    return lst
