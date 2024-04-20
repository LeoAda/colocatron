from schema import *
import db


def create_user(display_name: str, username: str):
    user = User(display_name=display_name, username=username)
    db.set_user(user)
    return user


def create_transaction(
    sender_username: str,
    receiver_username: str,
    reason: str,
    amount: float,
    due_date: date,
):
    transaction = Transaction(
        sender_username=sender_username,
        receiver_username=receiver_username,
        reason=reason,
        amount=amount,
        due_date=due_date,
    )
    db.set_transaction(transaction)
    return transaction


def create_item(display_name: str, user_order: list[str], current_user: str):
    item = Item(
        display_name=display_name,
        user_order=user_order,
        current_user=current_user,
    )
    db.set_item(item)
    return item


def increment_item(item_name: str):
    item = db.get_item_by_name(item_name)
    item.increment_current()
    db.set_item(item)
    return item


def increment_task(task_name: str):
    task = db.get_task_by_name(task_name)
    task.increment_current()
    db.set_task(task)
    return task


def create_task(display_name: str, user_order: list[str], current_user: str):
    task = Task(
        display_name=display_name, user_order=user_order, current_user=current_user
    )
    db.set_task(task)
    return task
