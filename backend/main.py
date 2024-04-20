import json
import db
from schema import User, Item
from function import *


a = create_user(display_name="Yoda", username="MasterYoda")
b = create_user(display_name="Vader", username="DarthVader")
c = create_user(display_name="Luke", username="LukeSkywalker")

x = create_transaction(
    sender_username="MasterYoda",
    receiver_username="DarthVader",
    reason="For the force",
    amount=1000,
    due_date="2022-02-02",
)

light_saber = create_item(
    display_name="Light Saber",
    user_order=["MasterYoda", "DarthVader"],
    current_user="MasterYoda",
)
kyber_crystal = create_item(
    display_name="Kyber Crystal",
    user_order=["MasterYoda", "DarthVader"],
    current_user="MasterYoda",
)


practice_force = create_task(
    display_name="Practice the force",
    user_order=["MasterYoda", "DarthVader", "LukeSkywalker"],
    current_user="MasterYoda",
)


allitem = db.get_all_items()
print(allitem)

increment_task("practice_the_force")

test = db.get_task_by_current_user("DarthVader")
print(test)
