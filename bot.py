import asyncio
import toml
import os
import requests
import sys

from typing import Union
from typing import Tuple

from vkbottle import API, VKAPIError
from vkbottle.user import User, Message, run_multibot
from vkbottle.dispatch.rules import ABCRule
from vkbottle.tools.dev.mini_types.base import BaseMessageMin
# Работа с конфигом: чтение из него
with open("config.toml", "r", encoding="utf-8") as f:
    if "token" in os.environ:
        config = dict(os.environ)
        for key, value in toml.load(f).items():
            if key not in config:
                config[key] = value
    else:
        config = toml.load(f)

with open("config_text.toml", "r", encoding="utf-8") as f:
    config_text = toml.load(f)

user = User()

# Кастомный рулз, который позволяет вызывать команды только определённым пользователям, которые прописаны в списке
class FromIdRule(ABCRule[BaseMessageMin]):
    def __init__(self, from_id: Union[list[int], int]):
        self.from_id = from_id

    async def check(self, event: BaseMessageMin) -> Union[dict, bool]:
        return event.from_id in self.from_id

user.labeler.custom_rules["from_id"] = FromIdRule

from_id_list = []
command_list = []

for i in config_text:
    command_list.append("/" + i)

################ Всё что выше - первоначальная настройка ############################################################

# Редактирует сообщение на то, что задал пользователь в конфиге
@user.on.message(from_id = from_id_list, text = command_list)
async def edit_message(message: Message):
    try:
        await message.ctx_api.messages.edit(
            peer_id=message.peer_id,
            message=config_text[message.text[1:]]["text"],
            attachment=config_text[message.text[1:]]["attachment"],
            message_id=message.id
        )
    except VKAPIError[100]:
        await message.ctx_api.messages.edit(
            peer_id=message.peer_id,
            message="ᅠ",
            message_id=message.id
        )

# Опубликовывает файл на сервер и редактирует сообщение в файл
async def upload_and_edit_message_in_file(message, null: int = 0, false: int = 0, true: int = 1):
    upload_server = dict(await message.ctx_api.docs.get_upload_server())["upload_url"]
    request = requests.post(upload_server, files={'file': open('chat_info.txt', 'rb')})
    uploaded_document = eval(str((await message.ctx_api.docs.save(file=request.json()['file'], title='chat_info')).json()))
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        attachment='doc' + str(uploaded_document['doc']['owner_id']) + '_' + str(uploaded_document['doc']['id']),
        message_id=message.id
    )
    await message.ctx_api.docs.delete(owner_id=uploaded_document['doc']['owner_id'], doc_id=uploaded_document['doc']['id'])
    os.remove("chat_info.txt")

# Записывает инфу о чате в файл
async def write_in_file_conversation_info(message, t_info, null: int = 0, false: int = 0, true: int = 1):
    file = open("chat_info.txt", "w", encoding="utf-8")
    t_all_member_ids = eval(t_info["preview"].json())["members"]
    t_member_ids = []
    t_group_ids = []
    for counter in range(0, len(t_all_member_ids)):
        if t_all_member_ids[counter] > 0:
            t_member_ids.append(t_all_member_ids[counter])
        else:
            t_group_ids.append(t_all_member_ids[counter] * (-1))
    file.write(str("Название беседы: " + str(eval(t_info["preview"].json())["title"]) + "\n\nID админа: " + str(
        eval(t_info["preview"].json())["admin_id"]) + "\n\nКоличество всех участников: " + str(
        eval(t_info["preview"].json())["members_count"]) + "\n\nКоличество людей: " + str(
        len(t_member_ids)) + "\n\nКоличество сообществ: " + str(len(t_group_ids)) + "\n\nID пользователей: "))
    for counter in range(0, len(t_member_ids)):
        file.write(str(t_member_ids[counter]) + ", ")
    file.write("\n\nID сообществ: ")
    for counter in range(0, len(t_group_ids)):
        file.write(str(t_group_ids[counter] * (-1)) + ", ")
    file.write("\n\nВызываемые ID пользователей: ")
    for counter in range(0, len(t_member_ids)):
        file.write("@id" + str(t_member_ids[counter]) + ", ")
    file.write("\n\nВызываемые ID сообществ: ")
    for counter in range(0, len(t_group_ids)):
        file.write("@club" + str(t_group_ids[counter]) + ", ")
    file.write("\n\nИмя и фамилия + (ID пользователя): ")
    t_member_names = await message.ctx_api.users.get(user_ids=t_member_ids)
    for counter in range(0, len(t_member_names)):
        file.write(str(eval(t_member_names[counter].json())['first_name']) + " " + str(
            eval(t_member_names[counter].json())['last_name']) + " (" + str(
            eval(t_member_names[counter].json())['id']) + "), ")
    file.write("\n\nНазвание + (ID сообщества): ")
    t_group_names = await message.ctx_api.groups.get_by_id(group_ids=t_group_ids)
    for counter in range(0, len(t_group_names)):
        file.write(str(eval(t_group_names[counter].json())['name']) + " (" + str(
            eval(t_group_names[counter].json())['id'] * (-1)) + "), ")
    file.close()
    await upload_and_edit_message_in_file(message)

# Редактирует сообщение на txt файл, в котором находится инфа о беседе
@user.on.chat_message(from_id = from_id_list, command = "get info")
async def get_chat_info(message: Message, null: int = 0, false: int = 0, true: int = 1):
    await write_in_file_conversation_info(message, dict(await message.ctx_api.messages.get_chat_preview(peer_id=message.peer_id)))

# Редактирует сообщение на txt файл, в котором находится инфа о беседе с ссылки
@user.on.message(from_id = from_id_list, command = ("get info", 1))
async def get_chat_info_by_link(message: Message, args: Tuple[str], none: int = 0, true: int = 1, null: int = 0, false: int = 0):
    await write_in_file_conversation_info(message, dict(await message.ctx_api.messages.get_chat_preview(link=args[0])))

# Перезапускает бота
@user.on.message(from_id = from_id_list, command = "restart")
async def restart_application(message: Message):
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

# Отображает список команд
@user.on.message(from_id = from_id_list, command = "help")
async def show_help(message: Message):
    global command_list
    custom_command_list = ""
    for i in range(0, len(command_list)):
        custom_command_list += command_list[i] + "\n"
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message="Кастомные команды для вызова функционала:\n\n" + custom_command_list + "\n" + "\nКоманды для вызова функционала:\n\n/get info - редактирует сообщение на txt файл, в котором находится список всех ID пользователей и групп в локальной беседе\n/get info <link> - редактирует сообщение на txt файл, в котором находится список всех ID пользователей и групп в беседе по ссылке приглашения\n/restart - перезапускает бота\n/help - выводит список со всеми командами",
        message_id=message.id
    )

################ Всё что ниже - настройка запуска и бота ############################################################
async def set_apis_from_config(apies):
    global from_id_list
    temp_token = ""
    counter = 0
    for letter_api in config["token"]:
        if letter_api != '\n':
            temp_token += letter_api
        elif letter_api == '\n' and config["token"][counter + 1] != '\n':
            apies.append(API(temp_token))
            from_id_list.append(int(dict(await User(temp_token).api.account.get_profile_info())['id']))
            temp_token = ""
        counter += 1
    apies.append(API(temp_token))
    from_id_list.append(int(dict(await User(temp_token).api.account.get_profile_info())['id']))

if __name__ == "__main__":
    apies = []
    set_token = asyncio.get_event_loop()
    set_token.run_until_complete(set_apis_from_config(apies))
    # user.loop_wrapper.auto_reload = True
    run_multibot(user, apis=apies)
