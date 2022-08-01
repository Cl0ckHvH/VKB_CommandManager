<h1 align="center">VKB Message editor by command</h1>
<p align="center">
    <img alt="Made with Python" src="https://img.shields.io/badge/Made%20with-Python-%23FFD242?logo=python&logoColor=white"></img>
	<img alt="Python version" src="https://img.shields.io/badge/python-3.10-blue.svg"></img>
</p>

## Получение токена
1. Перейдите на [сайт](https://vkhost.github.io/)
2. Нажмите на "Найстройки >>" > Сообщество > Выделяете все права > Получить
3. Даёте разрешение
4. Копируйте ваш токен в поле после слов access_token=, он начинается на vk1. (на момент написания readme) и заканчивается на "&", "&" не копировать
5. Готово

## Установка
### На Heroku
Понадобится аккаунт Heroku с привязанной картой (если хотите, чтобы он работал постоянно, без автооключений после определённого количества часов работы).

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Cl0ckHvH/VKB_Editmessage)

1. Нажмите на кнопку Deploy to Heroku
2. В меню выбора региона выберите Europe для лучшей производительности
3. Вводите в поля нужные настройки для бота, их можно и потом менять
3. Нажмите Deploy app
4. Готово

### Локально
1. Установите [Python](https://www.python.org/downloads/) версии не ниже 3.10. При установке убедитесь, что отметили галочку ![Add Python to PATH](https://sun9-east.userapi.com/sun9-17/s/v1/ig2/QxsAkYeUkCIWkOfZCyELhXQFbAKHiEdGXo4zWEkinzGT3pEtKV72GGs4tm6HnvgyC5Y1McmByppeXFKeX-PEc__Y.jpg?size=181x19&quality=96&type=album)
2. [Скачайте](https://github.com/Cl0ckHvH/VKB_Editmessage/archive/refs/heads/main.zip) и распакуйте
3. Откройте командную строку и введите следующую команду:
```sh
pip install -r requirements.txt --upgrade
```
4. Откройте файл `config.toml` любым текстовым редактором и настройте бота под себя
5. Для запуска введите в командную строку `bot.py`

### Если у вас Windows 7

Поддержка Python на Windows 7 прекратилась, начиная с версии 3.9, но всё таки нашёлся человек, который сделал поддержку для Windows 7. Скачать можно [тут](https://github.com/NulAsh/cpython/releases/tag/v3.10.1win7-1)
