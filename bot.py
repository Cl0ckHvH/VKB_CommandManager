import asyncio

import toml
import os
from typing import Union

from vkbottle import API, user
from vkbottle.user import User, Message, run_multibot
from vkbottle.dispatch.rules import ABCRule
from vkbottle.tools.dev.mini_types.base import BaseMessageMin

with open("config.toml", "r", encoding="utf-8") as f:
    if "token" in os.environ:
        config = dict(os.environ)
        for key, value in toml.load(f).items():
            if key not in config:
                config[key] = value
    else:
        config = toml.load(f)

user = User()

class FromIdRule(ABCRule[BaseMessageMin]):
    def __init__(self, from_id: Union[list[int], int]):
        self.from_id = from_id

    async def check(self, event: BaseMessageMin) -> Union[dict, bool]:
        return event.from_id in self.from_id

user.labeler.custom_rules["from_id"] = FromIdRule

def from_id_list_from_config(from_id_list):
    a = 0
    from_id_list.append("")
    for letter in config["from_id"]:
        if letter == ',' and letter != ' ':
            from_id_list.append("")
            from_id_list[a] = int(from_id_list[a])
            a += 1
        elif letter != ' ':
            from_id_list[a] += letter
    from_id_list[a] = int(from_id_list[a])

from_id_list = []
from_id_list_from_config(from_id_list)
@user.on.message(from_id = from_id_list, command = config["command"])
async def edit_message(message: Message):
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message=config["message"],
        attachment=config["attachment"],
        message_id=message.id
    )

@user.on.message(from_id = int(config["from_id"]), command = "gus")
async def gus(message: Message):
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        attachment="doc514714577_640721672",
        message_id=message.id
    )

async def set_apis_from_config(apies):
    temp_token = ""
    counter = 0
    for letter_api in config["token"]:
        if letter_api != '\n':
            temp_token += letter_api
        elif letter_api == '\n' and config["token"][counter + 1] != '\n':
            apies.append(API(temp_token))
            temp_token = ""
        counter += 1
    apies.append(API(temp_token))

if __name__ == "__main__":
    apies = []
    setup = asyncio.get_event_loop()
    setup.run_until_complete(set_apis_from_config(apies))
    user.loop_wrapper.auto_reload = True
    run_multibot(user, apis=apies)
