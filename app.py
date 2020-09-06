from flask import Flask, render_template, request, url_for, redirect, session, make_response, jsonify
import os
import requests 
import json
import hashlib
import uuid

api_url = os.environ['API_URL']

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())


def make_md5_hash(user_entered_password):
    result = hashlib.md5(user_entered_password.encode()) 
    password_hash = result.hexdigest()
    return password_hash


@app.route("/add_artists_options", methods=["GET"])
def select_option_update():
    all_artist = json.loads(requests.get(api_url+"/artist").content)
    data = {}
    for artst in all_artist:
        data[artst['name']] = artst['name']
    return make_response(jsonify(data), 200)


@app.route("/add_new_artist", methods=["POST"])
def add_a_new_artist():
    if 'userid' not in session:
        return redirect('/')
    artist_name = request.form['artist_name']
    artist_dob = request.form['artist_dob']
    artist_bio = request.form['artist_bio']        
    
    data = {
        "name":artist_name,
        "dob":artist_dob,
        "bio":artist_bio
    }
    respnse = requests.post(api_url+"/artist", data=json.dumps(data))
    if respnse.status_code == 200:
        respns = {"msg":"Success"}
        return make_response(jsonify(respns), 200)


@app.route("/top_10_songs", methods=["GET"])
def top_10_songs():    
    if 'userid' not in session:
        return redirect('/')
    top_songs_list = json.loads(requests.get(api_url+"/song?top=10").content)
    all_song = json.loads(requests.get(api_url+"/song").content)
    for sng in top_songs_list:
        artist_dc = json.loads(requests.get(api_url+"/artist/"+sng['id']).content)
        sng['artist'] = artist_dc.values()
    return render_template('top_songs.html',top_songs = top_songs_list, all_songs = [sng['name'] for sng in all_song])


@app.route("/top_10_artist", methods=["GET"])
def top_10_artist():    
    if 'userid' not in session:
        return redirect('/')
    top_artist_list = json.loads(requests.get(api_url+"/artist?top=10").content)
    all_song = json.loads(requests.get(api_url+"/song").content)
    for artst in top_artist_list:
        song_dc = json.loads(requests.get(api_url+"/song/"+artst['id']).content)
        artst['songs'] = song_dc.values()
    return render_template('top_artist.html',top_artist = top_artist_list, all_songs = [sng['name'] for sng in all_song])


@app.route('/rating',methods=['POST'])
def rating():
    if 'userid' not in session:
        return redirect('/')
    song_name = str(request.form.get('song_list')).replace("b'","").replace("'","")
    # get song_id
    rating_by_user = float(request.form.get('rangeInput'))
    user_id = str(session['userid']).replace("b'","").replace("'","")
    data = {
        "song_name" : song_name
    }
    song_id = str(requests.get(api_url+"/song?s_id=True",data=json.dumps(data) ).content)\
        [2:].replace("'","")
    if str(requests.get(api_url+"/rating/{}/{}".format(user_id,song_id))) == "True":
        print("Rating given already")
        return redirect(request.referrer)
    data={
        # user_id song_id rating
        "user_id" : user_id,
        "song_id" : song_id,
        "rating" : rating_by_user
    }
    signup_check = str(requests.post(api_url+"/rating", data=json.dumps(data)).content)
    return redirect(request.referrer)


@app.route('/adding_song', methods=["POST"])
def addingsong():
    if 'userid' not in session:
        return redirect('/')
    song_name = request.form.get('song_name')
    song_date = request.form.get('song_date')
    song_artist = request.form.getlist('artists')
    # print(song_artist)
    uploaded_file = request.files['cover_image']
    file_path = "./static/"
    data={
        "name":song_name,
        "date":song_date,
        "artist":song_artist
    }
    song_id = str(requests.post(api_url+"/song", data=json.dumps(data)).content)\
        .replace("b'","").replace("'","")    
    uploaded_file.filename = song_id+".jpg"
    uploaded_file.save(file_path+uploaded_file.filename)

    return redirect("/top_10_songs")


@app.route('/add_song')
def add_a_song():
    if 'userid' not in session:
        return redirect('/')
    all_artist = json.loads(requests.get(api_url+"/artist").content)
    all_song = json.loads(requests.get(api_url+"/song").content)
    return render_template('add_song.html', artist_names = [artst['name'] for artst in all_artist]\
         , all_songs = [sng['name'] for sng in all_song])


@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('mail')
    data = {
        "name":username,
        "mail" : email,
        "password" : password
    }
    signup_check = str(requests.post(api_url+"/signup", data=json.dumps(data)).content)
    if "-" in signup_check:
        return redirect("/")
    return "Email already exist"
    

@app.route('/check_login', methods=['POST'])
def check_login():
    mail = request.form.get('mail')
    password = request.form.get('password')
    data = {
        "mail" : mail,
        "password" : password
    }
    login_check = str(requests.get(api_url+"/login", data=json.dumps(data)).content)
    if "-" in login_check:
        session['userid'] = login_check
        session.permanent = False
        session.modified = True
        return redirect("/top_10_songs")
    return "Invalid Email or password..."


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/sign_up')
def sign_up():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0",port="5050", debug=True)