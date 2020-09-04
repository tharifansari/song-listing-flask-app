from flask import Flask, render_template, request, url_for, redirect, session
import os
import requests 
import json


api_url = os.environ['API_URL']

app = Flask(__name__)


@app.route("/top_10_songs", methods=["GET"])
def top_10_songs():    
    top_songs_list = json.loads(requests.get(api_url+"/song?top=10").content)
    for sng in top_songs_list:
        # print(str(api_url)+"/artist/"+str(sng))
        artist_dc = json.loads(requests.get(api_url+"/artist/"+sng['id']).content)
        sng['artist'] = artist_dc.values()
    return render_template('top_songs.html',top_songs = top_songs_list)


@app.route("/top_10_artist", methods=["GET"])
def top_10_artist():    
    top_artist_list = json.loads(requests.get(api_url+"/artist?top=10").content)
    for artst in top_artist_list:
        song_dc = json.loads(requests.get(api_url+"/song/"+artst['id']).content)
        artst['songs'] = song_dc.values()
    return render_template('top_artist.html',top_artist = top_artist_list)


if __name__ == '__main__':
    app.run(host="0.0.0.0",port="5050", debug=True)