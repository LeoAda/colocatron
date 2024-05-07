import db
from sqlalchemy.orm import sessionmaker, scoped_session
from function import *

engine = db.get_engine()
db.create_tables(engine)
session = scoped_session(sessionmaker(engine))


def create_mock() -> dict:
    new_user1 = add_user(
        session=session, name="John", username="johnd", password="pass"
    )
    new_user2 = add_user(
        session=session, name="Jane", username="janed", password="word"
    )
    new_item = add_item(session=session, name="Soap", current_user=new_user1)
    new_task = add_task(session=session, name="Vaccum", current_user=new_user2)
    new_transction = add_transaction(
        session=session,
        sender=new_user1,
        receiver=new_user2,
        reason="rent",
        due_date="2024-01-01",
        amount=100,
    )
    mock_ids = {
        "users": [new_user1.id, new_user2.id],
        "items": [new_item.id],
        "tasks": [new_task.id],
        "transactions": [new_transction.id],
    }
    return mock_ids


def delete_mock(mock_ids: dict):
    _ = [remove_user(session=session, user_id=user_id) for user_id in mock_ids["users"]]
    _ = [remove_item(session=session, item_id=item_id) for item_id in mock_ids["items"]]
    _ = [remove_task(session=session, task_id=task_id) for task_id in mock_ids["tasks"]]
    _ = [
        remove_transaction(session=session, transactions_id=transactions_id)
        for transactions_id in mock_ids["transactions"]
    ]


def delete_all():
    session.query(User).delete()
    session.query(Item).delete()
    session.query(Task).delete()
    session.query(Transaction).delete()
    session.commit()


def read_db():
    users = get_users(session)
    transaction = get_transactions(session)
    items = get_items(session)
    tasks = get_tasks(session)
    print(users)
    print(transaction)
    print(items)
    print(tasks)


# delete_all()
# create_mock()
read_db()
