from tinydb import TinyDB, Query
from schema import User, Item, Task, Transaction

db = TinyDB("backend/db.json")


def get_all_users():
    return [User(**user) for user in db.table("users").all()]


def set_user(user: User):
    result = db.table("users").upsert(
        user.format_to_db(), Query().username == user.username
    )


def get_all_items():
    return [Item(**item) for item in db.table("items").all()]


def get_items_by_current_user(current_user: str):
    query = db.table("items").search(Query().current_user == current_user)
    if query:
        return [Item(**item) for item in query]
    else:
        return []


def get_item_by_name(item_name: str):
    return Item(**db.table("items").get(Query().name == item_name))


def set_item(item: Item):
    result = db.table("items").upsert(item.format_to_db(), Query().name == item.name)


def delete_item(item_name: str):
    result = db.table("items").remove(Query().name == item_name)


def get_all_tasks():
    return [Task(**task) for task in db.table("tasks").all()]


def get_task_by_name(task_name: str):
    return Task(**db.table("tasks").get(Query().name == task_name))


def get_task_by_current_user(current_user: str):
    query = db.table("tasks").search(Query().current_user == current_user)
    if query:
        return [Task(**task) for task in query]
    else:
        return []


def set_task(task: Task):
    result = db.table("tasks").upsert(task.format_to_db(), Query().name == task.name)


def delete_task(task_name: str):
    result = db.table("tasks").remove(Query().name == task_name)


def get_all_transactions():
    return [
        Transaction(**transaction) for transaction in db.table("transactions").all()
    ]


def set_transaction(transaction: Transaction):
    result = db.table("transactions").upsert(
        transaction.format_to_db(), Query().id == transaction.id
    )


def delete_transaction(transaction_id: str):
    result = db.table("transactions").remove(Query().id == transaction_id)


def flush():
    db.drop_tables()
