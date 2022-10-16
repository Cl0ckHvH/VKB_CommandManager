import os
import sys
import asyncio
import requests

from config import *
from typing import Union, Tuple, Optional

from vkbottle import API, VKAPIError
from vkbottle.dispatch.rules import ABCRule
from vkbottle.http import SingleAiohttpClient
from vkbottle.user import User, Message, run_multibot
from vkbottle.tools.dev.mini_types.base import BaseMessageMin

user = User()

# Кастомный рулз, который позволяет вызывать команды только определённым пользователям, которые прописаны в списке
class FromIdRule(ABCRule[BaseMessageMin]):
    def __init__(self, from_id: Union[list[int], int]):
        self.from_id = from_id

    async def check(self, event: BaseMessageMin) -> Union[dict, bool]:
        return event.from_id in self.from_id

user.labeler.custom_rules['from_id'] = FromIdRule

from_id_list = []
command_list = []

for i in custom_settings:
    command_list.append(i)

################ Всё что выше - первоначальная настройка ############################################################

# Редактирует сообщение на то, что задал пользователь в конфиге
@user.on.message(from_id = from_id_list, text = command_list)
async def edit_message(message: Message):
    custom_command = message.text
    try:
        await message.ctx_api.messages.edit(
            peer_id=message.peer_id,
            message=custom_settings[custom_command]['text'],
            keep_forward_messages=1,
            attachment=custom_settings[custom_command]['attachment'],
            message_id=message.id
        )
    except VKAPIError[100]:
        await message.ctx_api.messages.edit(
            peer_id=message.peer_id,
            message='ᅠ',
            keep_forward_messages=1,
            message_id=message.id
        )

# Опубликовывает файл на сервер и редактирует сообщение в файл
async def upload_and_edit_message_in_file(message, file_name, null = None):
    upload_server = dict(await message.ctx_api.docs.get_upload_server())['upload_url']
    request = requests.post(upload_server, files={'file': open(file_name, 'rb')})
    uploaded_document = eval(str((await message.ctx_api.docs.save(file=request.json()['file'], title=file_name)).json()))
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        attachment=f"doc{uploaded_document['doc']['owner_id']}_{uploaded_document['doc']['id']}",
        keep_forward_messages=1,
        message_id=message.id
    )
    await message.ctx_api.docs.delete(owner_id=uploaded_document['doc']['owner_id'], doc_id=uploaded_document['doc']['id'])
    os.remove(file_name)

# Записывает инфу о чате в файл
async def write_in_file_conversation_info(message, t_info, file_name, t_link, null = None, true = True, false = False):
    file = open(file_name, 'w', encoding='utf-8')
    t_all_member_ids = eval(t_info['preview'].json())['members']
    t_member_ids = []
    t_group_ids = []
    for counter in range(0, len(t_all_member_ids)):
        if t_all_member_ids[counter] > 0:
            t_member_ids.append(t_all_member_ids[counter])
        else:
            t_group_ids.append(t_all_member_ids[counter] * (-1))
    file.write(f"""Название беседы: {(eval(t_info['preview'].json())['title']).encode('utf-8', 'replace').decode()}
    \nСсылка на приглашение: {t_link}
    \nID админа: {eval(t_info['preview'].json())['admin_id']}
    \nКоличество всех участников: {eval(t_info['preview'].json())['members_count']}
    \nКоличество людей: {len(t_member_ids)}
    \nКоличество сообществ: {len(t_group_ids)}
    \nID пользователей: """)
    for counter in range(0, len(t_member_ids)):
        file.write(f"{t_member_ids[counter]}, ")
    file.write('\n\nID сообществ: ')
    if len(t_group_ids) > 0:
        for counter in range(0, len(t_group_ids)):
            file.write(f"{t_group_ids[counter] * (-1)}, ")
    else: file.write('нету')
    file.write('\n\nВызываемые ID пользователей: ')
    for counter in range(0, len(t_member_ids)):
        file.write(f'@id{t_member_ids[counter]}, ')
    file.write('\n\nВызываемые ID сообществ: ')
    if len(t_group_ids) > 0:
        for counter in range(0, len(t_group_ids)):
            file.write(f"@club{t_group_ids[counter]}, ")
    else: file.write('нету')
    file.write('\n\nИмя и фамилия + (ID пользователя): ')
    t_member_names = await message.ctx_api.users.get(user_ids=t_member_ids)
    for counter in range(0, len(t_member_names)):
        file.write(f"{eval(t_member_names[counter].json())['first_name']} {eval(t_member_names[counter].json())['last_name']} ({eval(t_member_names[counter].json())['id']}), ")
    file.write('\n\nНазвание + (ID сообщества): ')
    if len(t_group_ids) > 0:
        t_group_names = await message.ctx_api.groups.get_by_id(group_ids=t_group_ids)
        for counter in range(0, len(t_group_names)):
            file.write(f"{eval(t_group_names[counter].json())['name']} ({eval(t_group_names[counter].json())['id'] * (-1)}), ")
    else: file.write('нету')
    file.write('\n\nИмя и фамилия пользователей: ')
    for counter in range(0, len(t_member_names)):
        file.write(f"{eval(t_member_names[counter].json())['first_name']} {eval(t_member_names[counter].json())['last_name']}, ")
    file.write('\n\nНазвание сообществ: ')
    if len(t_group_ids) > 0:
        t_group_names = await message.ctx_api.groups.get_by_id(group_ids=t_group_ids)
        for counter in range(0, len(t_group_names)):
            file.write(f"{eval(t_group_names[counter].json())['name']}, ")
    else: file.write('нету')
    file.close()
    await upload_and_edit_message_in_file(message, file_name)

# Редактирует сообщение на txt файл, в котором находится инфа о беседе
@user.on.chat_message(from_id = from_id_list, command = 'get info')
async def get_chat_info(message: Message):
    try: invite_link = dict(await message.ctx_api.messages.get_invite_link(peer_id=message.peer_id))['link']
    except: invite_link = 'нету'
    await write_in_file_conversation_info(message, dict(await message.ctx_api.messages.get_chat_preview(peer_id=message.peer_id)), 'chat_info.txt', invite_link)

# Редактирует сообщение на txt файл, в котором находится инфа о беседе с ссылки
@user.on.message(from_id = from_id_list, command = ('get info', 1))
async def get_chat_info_by_link(message: Message, args: Tuple[str]):
    await write_in_file_conversation_info(message, dict(await message.ctx_api.messages.get_chat_preview(link=args[0])), 'chat_info.txt', args[0])

@user.on.message(from_id = from_id_list, text = ('/audio <audio>'))
async def audio_message(message: Message, audio: Optional[str] = None, null = None):
    try: reply_message_id = dict(message.reply_message)['id']
    except: reply_message_id = None
    try:
        upload_server = dict(await message.ctx_api.docs.get_messages_upload_server(type = 'audio_message', peer_id=message.peer_id))['upload_url']
        request = requests.post(upload_server, files={'file': open((f"Audio\\{audio}.ogg"), 'rb')})
        uploaded_document = eval(str((await message.ctx_api.docs.save(file=request.json()['file'], title=(f"{audio}.ogg"))).json()))
        await message.ctx_api.messages.send(
            random_id = 0,
            peer_id=message.peer_id,
            attachment=f"doc{uploaded_document['audio_message']['owner_id']}_{uploaded_document['audio_message']['id']}",
            reply_to=reply_message_id
        )
        await message.ctx_api.docs.delete(owner_id=uploaded_document['audio_message']['owner_id'], doc_id=uploaded_document['audio_message']['id'])
        await message.ctx_api.messages.delete(message_ids = message.id, delete_for_all = 1, peer_id = message.peer_id)
    except VKAPIError[15]:
        await message.ctx_api.messages.delete(message_ids=message.id, peer_id=message.peer_id)
    except FileNotFoundError:
        await message.ctx_api.messages.edit(peer_id=message.peer_id,message=(f"Can't send audio, reason: No such file or directory: Audio\\{audio}.ogg"),message_id=message.id)
        await asyncio.sleep(2.0)
        try:
            await message.ctx_api.messages.delete(message_ids=message.id, delete_for_all=1, peer_id=message.peer_id)
        except VKAPIError[15]:
            await message.ctx_api.messages.delete(message_ids=message.id, peer_id=message.peer_id)

# Перезапускает бота
@user.on.message(from_id = from_id_list, command = 'restart')
async def restart_application(message: Message):
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

# Отображает список команд
@user.on.message(from_id = from_id_list, command = 'help')
async def show_help(message: Message):
    global command_list
    t_command_list = ''
    for i in range(0, len(command_list)):
        t_command_list += f"{command_list[i]}\n"
    await message.ctx_api.messages.edit(
        peer_id=message.peer_id,
        message=f"""Кастомные команды для вызова функционала:
        \n{t_command_list}
        Команды для вызова функционала:
        \n/get info - редактирует сообщение на txt файл, в котором находится список всех ID пользователей и групп в локальной беседе
        /get info <link> - редактирует сообщение на txt файл, в котором находится список всех ID пользователей и групп в беседе по ссылке приглашения
        /audio <audio name> - отправляет голосовое сообщение. <audio name> - название файла в папке Audio в формате .ogg. Ограничения: частота дискретизации — 16 кГц, битрейт — 16 кбит/с, длительность — не более 5 минут, моно.
        /restart - перезапускает бота
        /kick all - кикает всех из беседы (при наличия админки)
        /get photos <owner_id> <album_id> - получает список фотографий в виде текста "photo<owner_id>_<photo_id>". Используется для вставки в спам бот"
        /help - выводит список со всеми командами""",
        message_id=message.id
    )

@user.on.chat_message(from_id = from_id_list, command = 'kick all')
async def kick_everyone(message: Message, null = None, true = True):
    t_all_member_ids = eval((dict(await message.ctx_api.messages.get_chat_preview(peer_id=message.peer_id)))['preview'].json())['members']
    for i in range(0, len(t_all_member_ids)):
        try:
            if message.from_id != int(t_all_member_ids[i]):
                await message.ctx_api.messages.remove_chat_user(chat_id=(message.peer_id - 2000000000),member_id=int(t_all_member_ids[i]))
        except VKAPIError[925]: break
        except VKAPIError[15]:
            try:
                await message.ctx_api.request('messages.setMemberRole', {'peer_id':message.peer_id, 'member_id':int(t_all_member_ids[i]), 'role':'member'})
                i -= 1
            except: pass
        except VKAPIError: pass

@user.on.message(from_id = from_id_list, command = ('get photos', 2))
async def get_photos(message: Message, args: Tuple[str], null = None, false = False):
    t_photo_list = eval((await message.ctx_api.photos.get(owner_id=args[0], album_id=args[1])).json())['items']
    file = open('photo_list.txt', 'w', encoding='utf-8')
    file.write(f"Количество фотографий в альбоме: {len(t_photo_list)}\n\nID фотографий: ")
    for i in range(0, len(t_photo_list)):
        file.write(f"\'photo{args[0]}_{t_photo_list[i]['id']}\', ")
    file.close()
    await upload_and_edit_message_in_file(message, 'photo_list.txt')

################ Всё что ниже - настройка запуска и бота ############################################################
async def set_apis_from_config(apies = [], false = False, true = True, null = None):
    global from_id_list
    http = SingleAiohttpClient()
    for i in range(0, len(token)):
        apies.append(API(token[i]))
        api = API(token=token[i], http_client=http)
        from_id_list.append(eval(((await api.users.get())[0]).json())['id'])
        await api.http_client.close()
    return apies

if __name__ == '__main__':
    apies = asyncio.get_event_loop().run_until_complete(set_apis_from_config())
    run_multibot(user, apis=apies)
