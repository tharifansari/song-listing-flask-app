from flask import Flask, render_template, request, url_for, redirect, session
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

@app.route("/top_10_songs", methods=["GET"])
def top_10_songs():    
    # print(session['userid'])
    if 'userid' not in session:
        return redirect('/')
    top_songs_list = json.loads(requests.get(api_url+"/song?top=10").content)
    for sng in top_songs_list:
        # print(str(api_url)+"/artist/"+str(sng))
        artist_dc = json.loads(requests.get(api_url+"/artist/"+sng['id']).content)
        sng['artist'] = artist_dc.values()
    return render_template('top_songs.html',top_songs = top_songs_list)


@app.route("/top_10_artist", methods=["GET"])
def top_10_artist():    
    if 'userid' not in session:
        return redirect('/')
    top_artist_list = json.loads(requests.get(api_url+"/artist?top=10").content)
    for artst in top_artist_list:
        song_dc = json.loads(requests.get(api_url+"/song/"+artst['id']).content)
        artst['songs'] = song_dc.values()
    return render_template('top_artist.html',top_artist = top_artist_list)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/sign_up')
def sign_up():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')


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
    return "Invalid Email"
    

# @app.route('/change_password', methods=['GET', 'POST'])
# def change_password():
#     if request.method == 'GET':
#         return render_template('change_password.html')
#     else:
#         username = request.form.get('username')
#         old_password = request.form.get('old_password')
#         new_password = request.form.get('new_password')

#         search_result = db.search(User.username == username)
#         if len(search_result) == 0:
#             return 'incorrect username.'
#         else:
#             old_password_hash = make_md5_hash(old_password)
#             correct_password_hash = search_result[0]['password']
#             if old_password_hash == correct_password_hash:
 
#                 result = db.update({
#                     'password': make_md5_hash(new_password)}, 
#                     User.username == username
#                     )
#                 print(result)
#                 return redirect(url_for('home'))
#             else:
#                 return 'wrong password.'


if __name__ == '__main__':
    app.run(host="0.0.0.0",port="5050", debug=True)