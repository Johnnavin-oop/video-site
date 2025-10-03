from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os, sqlite3, datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        views INTEGER DEFAULT 0,
        upload_time TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    filter = request.args.get('filter', 'latest')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if filter == 'latest':
        c.execute("SELECT * FROM videos ORDER BY upload_time DESC")
    elif filter == 'old':
        c.execute("SELECT * FROM videos ORDER BY upload_time ASC")
    elif filter == 'views':
        c.execute("SELECT * FROM videos ORDER BY views DESC")
    else:
        c.execute("SELECT * FROM videos")
    videos = c.fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE title LIKE ?", ('%' + query + '%',))
    videos = c.fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

@app.route('/video/<int:video_id>')
def video(video_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE videos SET views = views + 1 WHERE id = ?", (video_id,))
    conn.commit()
    c.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    video = c.fetchone()
    conn.close()
    return render_template('video.html', video=video)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect('/upload')
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('admin'):
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        video = request.files['video']
        filename = secure_filename(video.filename)
        video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO videos (title, filename, upload_time) VALUES (?, ?, ?)",
                  (title, filename, datetime.datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('upload.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)