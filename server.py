from flask import Flask, render_template, request, redirect, url_for, session, jsonify,flash
import sqlite3
import subprocess
import traceback
import threading  # For safely managing processes

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Store running process globally
running_process = None
process_lock = threading.Lock()

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS snippets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        code TEXT NOT NULL,
                        language TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()


@app.route('/save_code', methods=['POST'])
def save_code():
    if 'user' not in session:
        return jsonify({'message': 'Login required'}), 401

    data = request.json
    code = data.get('code', "").strip()  # Ensure it's not empty
    language = data.get('language', "").strip()
    username = session['user']

    print(f"🔹 Received data: {data}")  # Debugging
    print(f"🔹 Saving Code: '{code}', Language: '{language}', Username: '{username}'")

    if not code:
        return jsonify({'message': 'Code cannot be empty'}), 400  # Prevent saving empty code

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO snippets (username, code, language) VALUES (?, ?, ?)", 
                   (username, code, language))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Code saved successfully'})

@app.route('/snippets/<int:id>', methods=['DELETE'])
def delete_snippet(id):
    if 'user' not in session:
        return jsonify({'message': 'Login required'}), 401

    username = session['user']
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Check if snippet exists and belongs to the user
    cursor.execute("SELECT id FROM snippets WHERE id = ? AND username = ?", (id, username))
    snippet = cursor.fetchone()

    if snippet:
        cursor.execute("DELETE FROM snippets WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Snippet deleted successfully'})
    else:
        conn.close()
        return jsonify({'message': 'Snippet not found or unauthorized'}), 403



@app.route('/snippets', methods=['GET'])
def view_snippets():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, code, language FROM snippets WHERE username = ?", (username,))
    snippets = [{'id': row[0], 'code': row[1], 'language': row[2]} for row in cursor.fetchall()]
    conn.close()

    return render_template('snippets.html', snippets=snippets)

@app.route('/snippets/<int:id>', methods=['GET'])
def get_snippet(id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT code, language FROM snippets WHERE id = ?", (id,))
    snippet = cursor.fetchone()
    conn.close()

    if snippet:
        print(f"Snippet {id} found: {snippet}")
        return render_template('view_snippet.html', code=snippet[0], language=snippet[1])
    else:
        return "Snippet not found", 404

@app.route("/", methods=['GET'])
def main():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username  # Store user in session
            return redirect(url_for('main'))
        else:
            return "Invalid credentials. Try again."

    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repassword=request.form['repassword']
        if password!=repassword:
            # flash("Passwords do not match! Try again.", "error")
            return render_template("signup.html", message="Passwords do not match!")
        
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already taken. Choose another one."

    return render_template("signup.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main'))

@app.route('/runcode', methods=['POST'])
def run_code():
    global running_process

    python_code = request.json.get('code')  # Get Python code from request
    try:
        with process_lock:
            if running_process and running_process.poll() is None:
                return jsonify({'output': None, 'error': "A process is already running. Stop it first."})

            # Start subprocess
            running_process = subprocess.Popen(['python', '-c', python_code],
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               text=True)
        
        stdout, stderr = running_process.communicate()

        with process_lock:
            running_process = None  # Clear after execution

        if stderr:
            return jsonify({'output': None, 'error': stderr})
        return jsonify({'output': stdout, 'error': None})

    except Exception as e:
        return jsonify({'output': None, 'error': traceback.format_exc()})

@app.route('/stop_execution', methods=['POST'])
def stop_execution():
    global running_process

    with process_lock:
        if running_process and running_process.poll() is None:  # Check if running
            running_process.terminate()  # Stop the process
            running_process = None  # Clear process reference
            return jsonify({"message": "Execution stopped."})

    return jsonify({"message": "No execution to stop."})

if __name__ == '__main__':
    app.run(debug=True, port=5500)
