from typing import Union
from sqlalchemy import create_engine, ForeignKey, ForeignKey, Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from flask_login import UserMixin

class Base(DeclarativeBase):
    pass


class User(Base,UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    sended_transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="sender", foreign_keys="Transaction.sender_id"
    )
    received_transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="receiver", foreign_keys="Transaction.receiver_id"
    )
    items: Mapped[list["Item"]] = relationship(back_populates="current_user")
    tasks: Mapped[list["Task"]] = relationship(back_populates="current_user")
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, username={self.username!r}, items=[{", ".join([str(item.name) for item in self.items])}], tasks=[{", ".join([str(task.name) for task in self.tasks])}], sended_transactions=[{", ".join([str(transaction) for transaction in self.sended_transactions])}], received_transactions=[{", ".join([str(transaction) for transaction in self.received_transactions])}])"

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

    def __str__(self) -> str:
        return f"{self.sender!s} -> {self.receiver!s} - {self.amount} - {self.reason}"
    
    def __repr__(self) -> str:
        return f"Transaction(id={self.id!r}, send={self.sender!s}, receiver_id={self.receiver!s}, reason={self.reason!r}, due_date={self.due_date!r}, amount={self.amount!r}, sender_approved={self.sender_approved!r}, receiver_approved={self.receiver_approved!r})"


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    emoji: Mapped[str] = mapped_column(default=":shopping_bags:")
    current_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    current_user: Mapped["User"] = relationship(back_populates="items")

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Item(id={self.id!r}, name={self.name!r}, emoji={self.emoji!r}, current_user_id={self.current_user_id!r}, current_user={self.current_user!s})"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    emoji: Mapped[str] = mapped_column(default=":broom:")
    current_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    current_user: Mapped["User"] = relationship(back_populates="tasks")

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, name={self.name!r}, emoji={self.emoji!r}, current_user_id={self.current_user_id!r}, current_user={self.current_user!s})"


def get_engine():
    db_path = "sqlite:///db.sqlite"
    engine = create_engine(db_path, echo=False)
    return engine


def create_tables(engine):
    Base.metadata.create_all(engine)
