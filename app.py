from flask import Flask, render_template, request, redirect

app = Flask(__name__)

messages = []

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/chat", methods=["GET","POST"])
def chat():
    if request.method == "POST":
        msg = request.form["message"]
        messages.append(msg)
    return render_template("chat.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
