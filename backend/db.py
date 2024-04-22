from typing import Union
from sqlalchemy import create_engine, ForeignKey, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()
    sended_transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="sender", foreign_keys="Transaction.sender_id"
    )
    received_transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="receiver", foreign_keys="Transaction.receiver_id"
    )
    items: Mapped[list["Item"]] = relationship(back_populates="current_user")
    tasks: Mapped[list["Task"]] = relationship(back_populates="current_user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, username={self.username!r}, items=[{", ".join([str(item.name) for item in self.items])}], tasks=[{", ".join([str(task.name) for task in self.tasks])}])"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    sender: Mapped["User"] = relationship(
        "User", back_populates="sended_transactions", foreign_keys=[sender_id]
    )
    receiver: Mapped["User"] = relationship(
        "User", back_populates="received_transactions", foreign_keys=[receiver_id]
    )
    reason: Mapped[str] = mapped_column()
    due_date: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column()
    sender_approved: Mapped[bool] = mapped_column()
    receiver_approved: Mapped[bool] = mapped_column()

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    current_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    current_user: Mapped["User"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return f"Item(id={self.id!r}, name={self.name!r}, current_user_id={self.current_user_id!r})"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    current_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    current_user: Mapped["User"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, name={self.name!r}, current_user_id={self.current_user_id!r})"

Actionable = Union[Item, Task]




def assign_to_next_user(session: Session, actionable: Actionable ):
    users = session.query(User).all()
    # Get current user
    current_user = actionable.current_user
    current_index = users.index(current_user)

    # Get next user
    next_index = (current_index + 1) % len(users)
    next_user = users[next_index]

    # Assign item to next user and remove from the current user
    current_user.items.remove(actionable)
    actionable.current_user = next_user
    next_user.items.append(actionable)

    # Commit changes
    session.commit()

def get_engine():
    db_path = "sqlite:///db.sqlite"
    engine = create_engine(db_path, echo=False)
    return engine
    
def create_tables(engine):
    Base.metadata.create_all(engine)

with Session(engine) as session:
    new_user1 = User(name="John", username="johnd")
    session.add(new_user1)
    new_user2 = User(name="Jane", username="janed")
    session.add(new_user2)
    new_item = Item(name="Item1", current_user=new_user1)
    session.add(new_item)
    session.commit()

with Session(engine) as session:
    users = session.query(User).all()
    print(users)

    items = session.query(Item).all()
    print(items)

    assign_to_next_user(session, items[0])

    items = session.query(Item).all()
    print(items)

    users = session.query(User).all()
    print(users)
