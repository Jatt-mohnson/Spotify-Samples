import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# import json
# from spotipy.util import prompt_for_user_token
from spotipy import util
from whosampled_scrape import *
# from config import *
import os


def parse_link(uri):
    if 'https:' in uri:
        uri = uri.split('/')[-1].split('?')[0]
    if 'spotify:' in uri:
        uri = uri.split(':')[2]
    return uri


def call_api(username, scope='playlist-modify-public'):
    client = '0db9481579f84081a98e19d819ecadc3'
    secret = 'd8534eebbefe4b31baf794b167688a39'
    token = util.prompt_for_user_token(username, scope, client_id=client, client_secret=secret, redirect_uri='http://google.com/')
    return token


def make_description(spot_dict):
    unfound = spot_dict['unfound']
    rate = spot_dict['rate']
    summary = 'Samples Not on Spotify: {} \nPercentage of Samples Added: {}%'.format(unfound, round(rate, 3))
    return summary


def read_playlist(uri, sp, link=None):
    username = 1285786764
    playlist_id = parse_link(uri)
    og_tracks = []
    results = sp.user_playlist(username, playlist_id)
    for i in results['tracks']['items']:
        artists = [j['name'] for j in i['track']['artists']]
        og_tracks.append({'artist' : artists, 'track':i['track']['name'].replace('Instrumental', '')})
    return og_tracks


def read_song(uri, sp):
    song_id = parse_link(uri)
    og_tracks = []
    results = sp.track(song_id)
    og_tracks.append({'artist': results['artists'][0]['name'], 'track':results['name'].replace('Instrumental', '')})
    return og_tracks


def read_album(uri, sp):
    album_id = parse_link(uri)
    og_tracks = []
    results = sp.album_tracks(album_id)
    for i in results['items']:
        artists = [j['name'] for j in i['artists']]
        og_tracks.append({'artist': artists, 'track':i['name'].replace('Instrumental', '')})
    return og_tracks


def get_sample_data(uri, sp):
    if 'playlist' in uri:
        loaded_playlist = read_playlist(uri, sp)
    elif 'album' in uri:
        loaded_playlist = read_album(uri, sp)
    elif 'track' in uri:
        loaded_playlist = read_song(uri, sp)
    new_playlist_tracks = get_whosampled_playlist(loaded_playlist)
    return new_playlist_tracks


def get_spotify_ids(whosampled_playlist, sp):
    id_list = []
    unfound_list= []
    for i in whosampled_playlist:
        sub_list = []
        artist = i['artist'].lower()
#         print('NEW SAMPLE: {} by {}'.format(i['title'], artist))
        result = sp.search(q='artist:' + artist + ' track:' + i['title'], type='track', limit=50)['tracks']['items']
        # result = sp.search(i['title'], limit=50)['tracks']['items']
        for j in result:
            if j['artists'][0]['name'].lower() == artist:
                sub_list.append(j['id'])
                break
        if sub_list:
            id_list.append(sub_list[0])
        else:
            unfound_list.append((i['title']+' by '+artist))
    location_rate = 1 - len(unfound_list)/len(whosampled_playlist)
    return {'ids': id_list, 'unfound': unfound_list, 'rate': location_rate}

def create_and_populate(username, new_playlist_name, spotify_dict, sp):
    playlist = sp.user_playlist_create(username, new_playlist_name)
    playlist_id = playlist["id"]
    files = os.listdir('playlist_data/')
    for f in files:
        os.remove('playlist_data/'+f)
    os.rename('samples.csv', 'playlist_data/' + playlist_id + '.csv')
    sp.user_playlist_add_tracks(username, playlist_id, spotify_dict['ids'], None) #populate playlist with all samples
    return playlist_id

def get_new_sample_playlist(uri, new_playlist_name, user):
    token = call_api(user, 'playlist-modify-public')
    sp2 = spotipy.Spotify(auth=token)
    new_playlist_tracks = get_sample_data(uri, sp2)
    print('\nChecking Spotify for Samples:\n')
    for i in new_playlist_tracks:
        print(i['title']+' by '+ i['artist'])
    spotify_dict = get_spotify_ids(new_playlist_tracks, sp2)
#     descript = make_description(spotify_dict)
    new_playlist = create_and_populate(user, new_playlist_name, spotify_dict, sp2)
    print('\nNew playlist "{}" created!'.format(new_playlist_name))
#     sp2.user_playlist_change_details(username, playlist_id, name=new_playlist_name, public=None, collaborative=None,description=description)
    return new_playlist

def run_program():
    username = 1285786764
    # uri = sys.argv[1]
    # name = sys.argv[2]
    uri = "spotify:playlist:6uLRFki6ras4ns4VLs3dTF"
    name = input('Please enter the name of your new sample playlist\n')

    new_playlist = get_new_sample_playlist(uri, name, username)
    return new_playlist

run_program()
