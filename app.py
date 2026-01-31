from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

BASE_DIR = "users"
os.makedirs(BASE_DIR, exist_ok=True)

def user_dir(username):
    return os.path.join(BASE_DIR, username)

def subject_file(username, subject):
    return os.path.join(user_dir(username), f"{subject}.txt")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        udir = user_dir(username)
        os.makedirs(udir, exist_ok=True)
        pwd_file = os.path.join(udir, "password.txt")

        # Register / Login logic
        if not os.path.exists(pwd_file):
            with open(pwd_file, "w") as f:
                f.write(password)
        else:
            with open(pwd_file, "r") as f:
                if f.read() != password:
                    return "❌ Wrong Password"

        session["user"] = username
        return redirect(url_for("notes"))

    return render_template("login.html")

@app.route("/notes", methods=["GET", "POST"])
def notes():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    subject = request.args.get("subject")

    notes_list = []
    if subject:
        file_path = subject_file(username, subject)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                notes_list = f.readlines()

    if request.method == "POST":
        note = request.form["note"]
        subject = request.form["subject"]
        time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        file_path = subject_file(username, subject)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{time} | {note}\n")
        return redirect(url_for("notes", subject=subject))

    return render_template("notes.html", user=username, subject=subject, notes=notes_list)

@app.route("/edit", methods=["POST"])
def edit_note():
    username = session["user"]
    subject = request.form["subject"]
    index = int(request.form["index"])
    new_text = request.form["new_note"]

    file_path = subject_file(username, subject)
    with open(file_path, "r", encoding="utf-8") as f:
        notes = f.readlines()

    time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    notes[index] = f"{time} | {new_text}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(notes)

    return redirect(url_for("notes", subject=subject))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
