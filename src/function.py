from typing import Union
from sqlalchemy.orm import Session
from db import User, Item, Task, Transaction, get_engine
from hashlib import sha256
import emoji


def add_user(session: Session, name: str, username: str, password: str) -> User:
    hash_password = sha256(password.encode("utf-8")).hexdigest()
    new_user = User(name=name, username=username, password=hash_password)
    session.add(new_user)
    session.commit()
    return new_user


def get_users(session: Session) -> list[User]:
    return session.query(User).all()


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.query(User).filter(User.username == username).first()


def remove_user(session: Session, user_id: int) -> None:
    user = get_user_by_id(session, user_id)
    for task in user.tasks:
        assign_task_to_next_user(session=session, task=task)
    for item in user.items:
        assign_item_to_next_user(session=session, item=item)
    for transaction in user.sended_transactions:
        remove_transaction(session=session, transaction_id=transaction.id)
    for transaction in user.received_transactions:
        remove_transaction(session=session, transaction_id=transaction.id)
    session.delete(user)
    session.commit()


def add_item(
    session: Session, name: str, current_user: User, emojized_emoji: str = "🛍"
) -> Item:
    emoji_code = emoji.demojize(emojized_emoji, language="alias")
    new_item = Item(name=name, current_user=current_user, emoji=emoji_code)
    session.add(new_item)
    session.commit()
    return new_item


def get_items(session: Session) -> list[Item]:
    return session.query(Item).all()


def get_item_by_id(session: Session, item_id: int) -> Item:
    return session.query(Item).filter(Item.id == item_id).first()


def remove_item(session: Session, item_id: int) -> None:
    item = get_item_by_id(session, item_id)
    session.delete(item)
    session.commit()


def add_task(
    session: Session, name: str, current_user: User, emojized_emoji: str = "🧹"
) -> Task:
    emoji_code = emoji.demojize(emojized_emoji, language="alias")
    new_task = Task(name=name, current_user=current_user, emoji=emoji_code)
    session.add(new_task)
    session.commit()
    return new_task


def get_tasks(session: Session) -> list[Task]:
    return session.query(Task).all()


def get_task_by_id(session: Session, task_id: int) -> Task:
    return session.query(Task).filter(Task.id == task_id).first()


def remove_task(session: Session, task_id: int) -> None:
    task = get_task_by_id(session, task_id)
    session.delete(task)
    session.commit()


def add_transaction(
    session: Session,
    sender: User,
    receiver: User,
    reason: str,
    amount: float,
    sender_approved: bool = False,
    receiver_approved: bool = False,
) -> Transaction:
    new_transaction = Transaction(
        sender=sender,
        receiver=receiver,
        reason=reason,
        amount=amount,
        sender_approved=sender_approved,
        receiver_approved=receiver_approved,
    )
    session.add(new_transaction)
    session.commit()
    return new_transaction


def get_transactions(session: Session) -> list[Transaction]:
    return session.query(Transaction).all()


def approved_receiver_transaction(session: Session, transaction: Transaction):
    with session.no_autoflush:
        transaction.receiver_approved = True
    session.commit()


def approved_sender_transaction(session: Session, transaction: Transaction):
    with session.no_autoflush:
        transaction.sender_approved = True
    session.commit()


def get_transaction_by_id(session: Session, transaction_id: int) -> Transaction:
    return session.query(Transaction).filter(Transaction.id == transaction_id).first()


def remove_transaction(session: Session, transaction_id: int) -> None:
    transaction = get_transaction_by_id(session, transaction_id)
    session.delete(transaction)
    session.commit()


def assign_item_to_next_user(session: Session, item: Item):
    with session.no_autoflush:
        users = get_users(session)
        # Get current user
        current_user = item.current_user
        current_index = users.index(current_user)

        # Get next user
        next_index = (current_index + 1) % len(users)
        next_user = users[next_index]

        # Assign item to next user and remove from the current user
        item.current_user = next_user
        next_user.items.append(item)
    # Commit changes
    session.commit()


def assign_task_to_next_user(session: Session, task: Task):
    with session.no_autoflush:
        users = get_users(session)
        # Get current user
        current_user = task.current_user
        current_index = users.index(current_user)

        # Get next user
        next_index = (current_index + 1) % len(users)
        next_user = users[next_index]

        # Assign task to next user and remove from the current user
        task.current_user = next_user
        next_user.tasks.append(task)
    # Commit changes
    session.commit()
