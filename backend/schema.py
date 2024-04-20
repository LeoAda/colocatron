from pydantic import BaseModel, ConfigDict, Field
import json
import hashlib
from datetime import date


class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    username: str
    display_name: str

    def __str__(self) -> str:
        return self.model_dump_json()

    def format_to_db(self) -> str:
        return self.model_dump(mode="json")


class Transaction(BaseModel):
    id: str = None
    sender_username: str
    receiver_username: str
    reason: str = ""
    due_date: date
    amount: float
    sender_approved: bool = False
    receiver_approved: bool = False

    # def __init__(self, **data):
    #     super().__init__(**data)
    #     self.id = hashlib.md5(
    #         "".join(
    #             [
    #                 self.sender_username,
    #                 self.receiver_username,
    #                 str(self.due_date),
    #                 str(self.amount),
    #             ]
    #         ).encode("utf-8")
    #     ).hexdigest()

    def format_to_db(self) -> str:
        return self.model_dump(mode="json")


class BaseClass(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    name: str = ""
    display_name: str
    user_order: list[str]
    current_user: str
    current_index: int = 0

    def __init__(self, **data):
        super().__init__(**data)
        self.name = self.display_name.replace(" ", "_").lower()

    def __str__(self) -> str:
        return self.model_dump_json()

    def format_to_db(self) -> str:
        return self.model_dump(mode="json")

    def increment_current(self):
        self.current_index = (self.current_index + 1) % len(self.user_order)
        self.current_user = self.user_order[self.current_index]


class Item(BaseClass):
    pass


class Task(BaseClass):
    pass
