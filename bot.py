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

user = User()

# Кастомный рулз, который позволяет вызывать команды только определённым пользователям, которые прописаны в списке
class FromIdRule(ABCRule[BaseMessageMin]):
    def __init__(self, from_id: Union[list[int], int]):
        self.from_id = from_id

    async def check(self, event: BaseMessageMin) -> Union[dict, bool]:
        return event.from_id in self.from_id

user.labeler.custom_rules["from_id"] = FromIdRule

# Настраивает from_id, беря его из файла
def from_id_list_from_config(from_id_list):
    temp_id = ""
    file = open('from_id_list.txt', 'r')
    file = file.read()
    for letter in file:
        if letter == ',' and letter != ' ':
            from_id_list.append(int(temp_id))
            temp_id = ""
        elif letter != ' ':
            temp_id += letter

from_id_list = []
from_id_list_from_config(from_id_list)
set_id_counter = 0

# Устанавливает from_id по токену
@user.on.message(command = "set_id")
async def set_id_from_token(message: Message, null: int = 0, false: int = 0, true: int = 1):
    global set_id_counter
    if set_id_counter == 0:
        from_id_list.clear()
        file = open('from_id_list.txt', 'w')
        file.close()
        await asyncio.sleep(1.0)
        file = open('from_id_list.txt', 'a')
        temp_id = eval((await message.ctx_api.users.get(fields='id'))[0].json())['id']
        from_id_list.append(int(temp_id))
        file.write(str(temp_id) + ', ')
        await asyncio.sleep(1.0)
        file.close
        set_id_counter = 1
        await message.ctx_api.messages.edit(peer_id=message.peer_id, message="ID-шники успешно установленны, всего их: " + str(len(from_id_list)), message_id=message.id)

################ Всё что выше - первоначальная настройка ############################################################

# Редактирует сообщение на то, что задал пользователь в конфиге
@user.on.message(from_id = from_id_list, command = config["command"])
async def edit_message(message: Message):
    try:
        await message.ctx_api.messages.edit(
            peer_id=message.peer_id,
            message=config["text"],
            attachment=config["attachment"],
            message_id=message.id
        )
    except VKAPIError[100]:
        await message.ctx_api.messages.edit(
            peer_id=message.peer_id,
            message="ᅠ",
            message_id=message.id
        )

# Редактирует сообщение на гифку buff gus
@user.on.message(from_id = from_id_list, command = "gus")
async def gus(message: Message):
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        attachment="doc514714577_640721672",
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
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message="Команды для вызова функционала:\n\n/" + config["command"] + " (кастомная команда) - редактирует сообщение на то, что Вы задали в конфиге\n/gus - редактирует сообщение на гифку buff gus\n/get_id - редактирует сообщение на txt файл, в котором находится список всех ID пользователей и групп в беседе\n/restart - перезапускает бота\n\nКоманды для редактирования кастомного функционала:\n\n/attachment remove - удаляет кастомное вложение\n/attachment edit <value> - устанавливает кастомное вложение на <value>\n/text remove - удаляет кастомный текст\n/text edit <value> - устанавливает кастомный текст на <value>\n/command edit <value> - устанавливает кастомную команду для вызова на <value>",
        message_id=message.id
    )

################ Команды для настройки конфига ######################################################################

# Функция для удаление любого параметра переменной из конфига
async def config_remove_item(parameter):
    f = open("config.toml", "r", encoding="utf-8")
    config_container = f.read()
    temp_config = config_container.replace(config[parameter], "")
    with open("config.toml", "w", encoding="utf-8") as f:
        f.write(temp_config)
    config[parameter] = ""

# Функция для удаление любого параметра переменной из конфига
async def config_edit_item(parameter, args):
    f = open("config.toml", "r", encoding="utf-8")
    config_container = f.read()
    temp_replace1 = parameter + " = \"" + str(config[parameter]) + "\""
    temp_replace2 = parameter + " = \"" + str(args) + "\""
    temp_config = config_container.replace(temp_replace1, temp_replace2)
    with open("config.toml", "w", encoding="utf-8") as f:
        f.write(temp_config)
    config[parameter] = args

# Удаляет вложение из конфига
@user.on.message(from_id = from_id_list, command = "attachment remove")
async def attachment_remove(message: Message):
    await config_remove_item("attachment")
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message="Кастомное вложение было удалено",
        message_id=message.id
    )
    await asyncio.sleep(1.0)
    await message.ctx_api.messages.delete(message_ids=message.id, delete_for_all=1)

# Изменяет вложение на любое из конфига
@user.on.message(from_id = from_id_list, command = ("attachment edit", 1))
async def attachment_edit(message: Message, args: Tuple[str]):
    await config_edit_item("attachment", args[0])
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message="Готово, кастомное вложение было изменено на:",
        attachment=args[0],
        message_id=message.id
    )
    await asyncio.sleep(1.0)
    await message.ctx_api.messages.delete(message_ids=message.id, delete_for_all=1)

# Удаляет текст из конфига
@user.on.message(from_id = from_id_list, command = "text remove")
async def text_remove(message: Message):
    await config_remove_item("text")
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message="Кастомный текст был удалён",
        message_id=message.id
    )
    await asyncio.sleep(1.0)
    await message.ctx_api.messages.delete(message_ids=message.id, delete_for_all=1)

# Изменяет текст на любое из конфига
@user.on.message(from_id = from_id_list, command = ("text edit", 1))
async def text_edit(message: Message, args: Tuple[str]):
    await config_edit_item("text", args[0])
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message="Готово, кастомный текст был изменён на: " + config["text"],
        message_id=message.id
    )
    await asyncio.sleep(1.0)
    await message.ctx_api.messages.delete(message_ids=message.id, delete_for_all=1)

# Изменяет команду вызова из конфига
@user.on.message(from_id = from_id_list, command = ("command edit", 1))
async def command_edit(message: Message, args: Tuple[str]):
    await config_edit_item("command", args[0])
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message="Готово, кастомная команда была изменена на: " + config["command"],
        message_id=message.id
    )
    await asyncio.sleep(1.0)
    await message.ctx_api.messages.delete(message_ids=message.id, delete_for_all=1)
    await restart_application(message)

################ Всё что ниже - настройка запуска и бота ############################################################
def set_apis_from_config(apies):
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
    set_apis_from_config(apies)
    # user.loop_wrapper.auto_reload = True
    run_multibot(user, apis=apies)
