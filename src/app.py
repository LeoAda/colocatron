import db
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import dotenv_values
import os
from function import *
from hashlib import sha256

import emoji

configs = {
    **dotenv_values(".env"),
    **os.environ,
}

engine = db.get_engine()
db.create_tables(engine)
session = scoped_session(sessionmaker(engine))

app = Flask(__name__)
app.secret_key = configs["SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(session, user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user_by_username(session, username)
        if user != None:
            if user.password == sha256(password.encode("utf-8")).hexdigest():
                login_user(user, remember=True)
                return redirect(url_for("home"))
            else:
                flash("Wrong password")
                return render_template("login.html")
        else:
            flash("Wrong username")
            return render_template("login.html")
    elif request.method == "GET":
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        user = add_user(session, name=name, username=username, password=password)
        return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("register.html")


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", current_user=current_user)


@app.route("/task", methods=["POST"])
@login_required
def task():
    if request.method == "POST":
        request_task_id = request.form.get("task_id")
        for user_task in current_user.tasks:
            if str(user_task.id) == request_task_id:
                assign_task_to_next_user(session=session, task=user_task)
                return redirect(url_for("home"))
        flash("Task not found")
        return redirect(url_for("home"))


@app.route("/task/add", methods=["POST"])
@login_required
def request_add_task():
    request_task_name = request.form.get("task_name")
    request_emoji = request.form.get("emoji")
    request_user_id = request.form.get("user_id")
    request_user = (
        get_user_by_id(session=session, user_id=request_user_id)
        if request_user_id
        else current_user
    )
    params = {
        "session": session,
        "name": request_task_name,
        "current_user": request_user,
    }
    if request_emoji:
        params["emojized_emoji"] = request_emoji
    add_task(**params)
    return redirect(request.referrer)


@app.route("/task/delete", methods=["POST"])
@login_required
def request_delete_task():
    request_task_id = int(request.form.get("task_id"))
    remove_task(session=session, task_id=request_task_id)
    return redirect(request.referrer)


@app.route("/item", methods=["POST"])
@login_required
def item():
    request_item_id = int(request.form.get("item_id"))
    for user_item in current_user.items:
        if user_item.id == request_item_id:
            assign_item_to_next_user(session=session, item=user_item)
            return redirect(url_for("home"))
    flash("Item not found")
    return redirect(url_for("home"))


@app.route("/item/add", methods=["POST"])
@login_required
def request_add_item():
    request_item_name = request.form.get("item_name")
    request_emoji = request.form.get("emoji")
    request_user_id = request.form.get("user_id")
    request_user = (
        get_user_by_id(session=session, user_id=request_user_id)
        if request_user_id
        else current_user
    )
    params = {
        "session": session,
        "name": request_item_name,
        "current_user": request_user,
    }
    if request_emoji:
        params["emojized_emoji"] = request_emoji
    add_item(**params)
    return redirect(request.referrer)


@app.route("/item/delete", methods=["POST"])
@login_required
def request_delete_item():
    request_item_id = int(request.form.get("item_id"))
    remove_item(session=session, item_id=request_item_id)
    return redirect(request.referrer)


@app.route("/transaction", methods=["POST"])
@login_required
def transaction():
    request_transaction_id = int(request.form.get("transaction_id"))
    request_transaction = get_transaction_by_id(
        session=session, transaction_id=request_transaction_id
    )
    if request_transaction.receiver_id == current_user.id:
        approved_receiver_transaction(session=session, transaction=request_transaction)
    elif request_transaction.sender_id == current_user.id:
        approved_sender_transaction(session=session, transaction=request_transaction)
    else:
        flash("Transaction not found")
    return redirect(url_for("home"))


@app.route("/transaction/add", methods=["POST"])
@login_required
def request_add_transaction():
    request_sender_id = request.form.get("sender_id")
    request_receiver_id = request.form.get("receiver_id")
    request_amount = float(request.form.get("amount"))
    request_reason = request.form.get("reason")
    sender = get_user_by_id(session=session, user_id=request_sender_id)
    receiver = get_user_by_id(session=session, user_id=request_receiver_id)
    add_transaction(
        session=session,
        sender=sender,
        receiver=receiver,
        reason=request_reason,
        amount=request_amount,
    )
    return redirect(request.referrer)


@app.route("/transaction/delete", methods=["POST"])
@login_required
def request_delete_transaction():
    request_transaction_id = int(request.form.get("transaction_id"))
    remove_transaction(session=session, transaction_id=request_transaction_id)
    return redirect(request.referrer)


@app.route("/history", methods=["GET"])
@login_required
def history():
    tasks = get_tasks(session=session)
    items = get_items(session=session)
    transactions = get_transactions(session=session)
    return render_template(
        "history.html", tasks=tasks, items=items, transactions=transactions
    )


@app.route("/manage", methods=["GET"])
@login_required
def manage():
    tasks = get_tasks(session=session)
    items = get_items(session=session)
    transactions = get_transactions(session=session)
    users = get_users(session=session)
    return render_template(
        "manage.html", tasks=tasks, items=items, transactions=transactions, users=users
    )


@app.route("/user/delete", methods=["POST"])
@login_required
def request_delete_user():
    request_user_id = int(request.form.get("user_id"))
    remove_user(session=session, user_id=request_user_id)
    return redirect(request.referrer)


@app.route("/admin", methods=["GET"])
@login_required
def admin():
    users = get_users(session=session)
    tasks = get_tasks(session=session)
    items = get_items(session=session)
    transactions = get_transactions(session=session)
    return render_template(
        "admin.html", users=users, tasks=tasks, items=items, transactions=transactions
    )


@app.template_filter("emojify")
def emojify(s):
    return emoji.emojize(s, language="alias")


@app.context_processor
def inject_configs():
    return configs


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
