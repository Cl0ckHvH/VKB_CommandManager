import toml
import os
from typing import Union

from vkbottle import API, user
from vkbottle.user import User, Message
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

user = User(token=config["token"])

class FromIdRule(ABCRule[BaseMessageMin]):
    def __init__(self, from_id: int = 0):
        self.from_id = from_id

    async def check(self, event: BaseMessageMin) -> Union[dict, bool]:
        return self.from_id == event.from_id

user.labeler.custom_rules["from_id"] = FromIdRule

@user.on.message(from_id = int(config["from_id"]), command = config["command"])
async def edit_message(message: Message):
    await user.api.messages.edit(
        peer_id=message.peer_id,
        message=config["message"],
        attachment=config["attachment"],
        message_id=message.id
    )

if __name__ == "__main__":
    user.loop_wrapper.auto_reload = True
    user.run_forever()