import os
import secrets
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(64)

# --- 📁 STORAGE DIRECTORIES ---
BASE_DIR = 'viro_supreme_storage'
CATEGORIES = ['images', 'videos', 'pdfs', 'links']
for cat in CATEGORIES:
    os.makedirs(os.path.join(BASE_DIR, cat), exist_ok=True)

# --- 🎨 SUPREME UI (AUTH + DASHBOARD) ---
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIRO SUPREME</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --bg: #000; --card-bg: #111; --text: #fff; --accent: #fff; }
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; font-family: 'Inter', sans-serif; }
        body { background: var(--bg); color: var(--text); margin: 0; padding: 0; overflow-x: hidden; }

        /* --- 🔐 AUTH STYLES --- */
        .auth-container { 
            position: fixed; inset: 0; background: #000; z-index: 9999; 
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            padding: 20px; transition: 0.5s;
        }
        .auth-box { 
            width: 100%; max-width: 350px; text-align: center; 
            border: 1px solid #222; padding: 30px; border-radius: 20px; background: #050505;
        }
        .auth-box h2 { font-size: 30px; letter-spacing: 5px; margin-bottom: 30px; font-weight: 200; }
        .input-group { position: relative; margin-bottom: 15px; }
        .input-group i { position: absolute; left: 15px; top: 15px; color: #444; }
        .auth-box input { 
            width: 100%; padding: 15px 15px 15px 45px; background: #111; border: 1px solid #222; 
            border-radius: 12px; color: #fff; font-size: 14px; outline: none; transition: 0.3s;
        }
        .auth-box input:focus { border-color: #fff; }
        .auth-btn { 
            width: 100%; padding: 15px; background: #fff; color: #000; border: none; 
            border-radius: 12px; font-weight: bold; margin-top: 20px; cursor: pointer;
        }
        .toggle-auth { margin-top: 20px; font-size: 12px; color: #666; cursor: pointer; }
        .toggle-auth span { color: #fff; text-decoration: underline; }

        /* --- 📱 DASHBOARD STYLES (v3 Improved) --- */
        header { padding: 30px 20px 10px; border-bottom: 1px solid #222; display: flex; justify-content: space-between; align-items: center; }
        .container { padding: 15px; padding-bottom: 100px; }
        .category-scroll { display: flex; gap: 10px; overflow-x: auto; padding: 10px 0; scrollbar-width: none; }
        .cat-chip { background: var(--card-bg); padding: 10px 20px; border-radius: 20px; text-decoration: none; color: #888; font-size: 13px; border: 1px solid #222; }
        .cat-chip.active { background: #fff; color: #000; font-weight: bold; }
        
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 10px; }
        .item-card { background: var(--card-bg); border-radius: 15px; overflow: hidden; border: 1px solid #222; }
        .preview { height: 140px; background: #0a0a0a; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .preview img, .preview video { width: 100%; height: 100%; object-fit: cover; }
        .info { padding: 10px; font-size: 10px; text-align: center; }
        
        .fab { position: fixed; bottom: 85px; right: 20px; background: #fff; color: #000; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; z-index: 100; box-shadow: 0 0 20px rgba(255,255,255,0.1); }
        .bottom-nav { position: fixed; bottom: 0; width: 100%; background: #000; border-top: 1px solid #222; display: flex; justify-content: space-around; padding: 15px 0; z-index: 1000; }
        .nav-item { color: #444; text-decoration: none; text-align: center; }
        .nav-item.active { color: #fff; }
        .nav-item span { display: block; font-size: 8px; margin-top: 5px; }
    </style>
</head>
<body>

    {% if not session.get('logged_in') %}
    <div class="auth-container" id="authUI">
        <div class="auth-box" id="loginForm">
            <h2>LOGIN</h2>
            <form action="/login" method="post">
                <div class="input-group">
                    <i class="fas fa-envelope"></i>
                    <input type="email" name="email" placeholder="Gmail Address" required>
                </div>
                <div class="input-group">
                    <i class="fas fa-lock"></i>
                    <input type="password" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="auth-btn">SIGN IN</button>
            </form>
            <div class="toggle-auth" onclick="toggleForm('signup')">Don't have an account? <span>Sign Up</span></div>
        </div>

        <div class="auth-box" id="signupForm" style="display:none;">
            <h2>SIGN UP</h2>
            <form action="/signup" method="post">
                <div class="input-group"><i class="fas fa-user"></i><input type="text" placeholder="Full Name" required></div>
                <div class="input-group"><i class="fas fa-envelope"></i><input type="email" placeholder="Gmail" required></div>
                <div class="input-group"><i class="fas fa-phone"></i><input type="tel" placeholder="Phone Number" required></div>
                <div class="input-group"><i class="fas fa-lock"></i><input type="password" placeholder="Password" required></div>
                <button type="submit" class="auth-btn">CREATE ACCOUNT</button>
            </form>
            <div class="toggle-auth" onclick="toggleForm('login')">Already have an account? <span>Sign In</span></div>
        </div>
    </div>
    {% endif %}

    <header>
        <div style="font-weight:900; letter-spacing:2px;">VIRO SUPREME</div>
        <a href="/logout" style="color:#666; text-decoration:none; font-size:12px;"><i class="fas fa-sign-out-alt"></i></a>
    </header>

    <div class="container">
        <div class="category-scroll">
            <a href="/?cat=images" class="cat-chip {{ 'active' if current_cat == 'images' }}">Images</a>
            <a href="/?cat=videos" class="cat-chip {{ 'active' if current_cat == 'videos' }}">Videos</a>
            <a href="/?cat=pdfs" class="cat-chip {{ 'active' if current_cat == 'pdfs' }}">PDF Docs</a>
            <a href="/?cat=links" class="cat-chip {{ 'active' if current_cat == 'links' }}">Servers</a>
        </div>

        <div class="grid">
            {% for item in items %}
            <div class="item-card">
                <div class="preview">
                    {% if current_cat == 'images' %}
                        <img src="/download/images/{{ item }}">
                    {% elif current_cat == 'videos' %}
                        <video controls muted><source src="/download/videos/{{ item }}" type="video/mp4"></video>
                    {% elif current_cat == 'pdfs' %}
                        <i class="fas fa-file-pdf" style="font-size:35px; color:#ff4444;"></i>
                    {% elif current_cat == 'links' %}
                        <i class="fas fa-link" style="font-size:25px;"></i>
                    {% endif %}
                </div>
                <div class="info">
                    <b>{{ item[:15] }}...</b>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <form action="/upload" method="post" enctype="multipart/form-data" id="upForm" style="display:none;">
        <input type="file" name="file" id="fileInput" onchange="document.getElementById('upForm').submit()">
    </form>
    
    <label for="fileInput" class="fab"><i class="fas fa-plus"></i></label>

    <div class="bottom-nav">
        <a href="/?cat=images" class="nav-item {{ 'active' if current_cat == 'images' }}"><i class="fas fa-image"></i><span>Photos</span></a>
        <a href="/?cat=videos" class="nav-item {{ 'active' if current_cat == 'videos' }}"><i class="fas fa-play"></i><span>Videos</span></a>
        <a href="/?cat=pdfs" class="nav-item {{ 'active' if current_cat == 'pdfs' }}"><i class="fas fa-file-pdf"></i><span>PDF</span></a>
        <a href="/?cat=links" class="nav-item {{ 'active' if current_cat == 'links' }}"><i class="fas fa-server"></i><span>Links</span></a>
    </div>

    <script>
        function toggleForm(type) {
            const login = document.getElementById('loginForm');
            const signup = document.getElementById('signupForm');
            if(type === 'signup') { login.style.display = 'none'; signup.style.display = 'block'; }
            else { login.style.display = 'block'; signup.style.display = 'none'; }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    cat = request.args.get('cat', 'images')
    items = os.listdir(os.path.join(BASE_DIR, cat)) if cat != 'links' else []
    return render_template_string(UI_TEMPLATE, items=items, current_cat=cat)

@app.route('/login', methods=['POST'])
def login():
    session['logged_in'] = True
    return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    session['logged_in'] = True
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        ext = file.filename.split('.')[-1].lower()
        target = 'pdfs' if ext == 'pdf' else ('videos' if ext in ['mp4','mkv','mov'] else 'images')
        file.save(os.path.join(BASE_DIR, target, file.filename))
    return redirect(url_for('index', cat=target))

@app.route('/download/<cat>/<name>')
def download(cat, name):
    return send_from_directory(os.path.join(BASE_DIR, cat), name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
