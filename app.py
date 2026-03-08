from flask import Flask, render_template, request, redirect, session
import sqlite3
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "securekey"

key = Fernet.generate_key()
cipher = Fernet(key)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT
    )""")

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users(username,password) VALUES (?,?)",(username,password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/chat", methods=["GET","POST"])
def chat():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        msg = request.form["message"]
        encrypted = cipher.encrypt(msg.encode())

        c.execute("INSERT INTO messages(username,message) VALUES (?,?)",
                  (session["user"], encrypted))
        conn.commit()

    c.execute("SELECT username,message FROM messages")

    messages = []
    for row in c.fetchall():
        decrypted = cipher.decrypt(row[1]).decode()
        messages.append((row[0], decrypted))

    conn.close()

    return render_template("chat.html",messages=messages)

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
