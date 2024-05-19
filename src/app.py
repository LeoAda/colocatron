import db
from flask import Flask, render_template, request, url_for, redirect, flash
from waitress import serve
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from sqlalchemy.orm import sessionmaker, scoped_session
from config import configs
from function import *
from utils import string_hash
import emoji


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


@login_manager.unauthorized_handler
def unauthorized_request():
    flash("Please login or register")
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember") == "remember"
        user = get_user_by_username(session, username)
        if user != None:
            if user.password == string_hash(password):
                login_user(user, remember=remember)
                return redirect(url_for("home"))
            else:
                flash("Wrong password")
                return render_template("login.html")
        else:
            flash("Wrong username")
            return render_template("login.html")
    elif request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        else:
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
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        else:
            return render_template("register.html")


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html", current_user=current_user)


@app.route("/task", methods=["POST"])
@login_required
def task():
    request_task_id = request.form.get("task_id")
    assign_task_to_next_user(session=session, task_id=request_task_id)
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


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
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


@app.route("/task/delete", methods=["POST"])
@login_required
def request_delete_task():
    request_task_id = int(request.form.get("task_id"))
    remove_task(session=session, task_id=request_task_id)
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


@app.route("/item", methods=["POST"])
@login_required
def item():
    request_item_id = int(request.form.get("item_id"))
    assign_item_to_next_user(session=session, item_id=request_item_id)
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


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
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


@app.route("/item/delete", methods=["POST"])
@login_required
def request_delete_item():
    request_item_id = int(request.form.get("item_id"))
    remove_item(session=session, item_id=request_item_id)
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


@app.route("/transaction", methods=["POST"])
@login_required
def transaction():
    request_transaction_id = int(request.form.get("transaction_id"))
    request_transaction = get_transaction_by_id(
        session=session, transaction_id=request_transaction_id
    )
    request_user_id = int(request.form.get("user_id", current_user.id))
    if request_transaction.receiver_id == request_user_id:
        approved_receiver_transaction(session=session, transaction=request_transaction)
    elif request_transaction.sender_id == request_user_id:
        approved_sender_transaction(session=session, transaction=request_transaction)
    else:
        flash("Transaction not found")
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


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
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


@app.route("/transaction/delete", methods=["POST"])
@login_required
def request_delete_transaction():
    request_transaction_id = int(request.form.get("transaction_id"))
    remove_transaction(session=session, transaction_id=request_transaction_id)
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


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
    return redirect(request.referrer) if request.referrer else redirect(url_for("home"))


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
    is_debug: bool = configs["MODE"] == "debug"
    host: str = configs["HOST"] if configs["HOST"] else "127.0.0.1"
    port: int = int(configs["PORT"]) if configs["PORT"] else 8080
    if is_debug:
        app.run(host=host, port=port, debug=True)
    else:
        serve(app, host=host, port=port)
