from flask import Flask, request, render_template_string, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "hardcoded-secret-key"  # Hardcoded secret

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return "<h1>Vulnerable Flask App</h1> <a href='/login'>Login</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SQL Injection vulnerability
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cur.execute(query)
        user = cur.fetchone()
        conn.close()
        
        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "<h3>Login Failed</h3>"
    return '''<form method='post'>
                Username: <input type='text' name='username'>
                Password: <input type='password' name='password'>
                <input type='submit'>
              </form>'''

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return f"<h1>Welcome {session['user']}</h1> <a href='/logout'>Logout</a>"

@app.route('/profile/<user_id>')
def profile(user_id):
    # Insecure Direct Object Reference (IDOR)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = cur.fetchone()
    conn.close()
    
    if user:
        return f"<h1>Profile of {user['username']}</h1>"
    else:
        return "User not found"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/xss')
def xss():
    comment = request.args.get('comment', '')  # Reflective XSS vulnerability
    return render_template_string(f"<h1>Comment:</h1><p>{comment}</p>")

if __name__ == '__main__':
    app.run(debug=True)
