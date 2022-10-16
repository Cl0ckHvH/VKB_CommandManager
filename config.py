token = ['']

custom_settings = {}

class Custom_commands:
    def __init__(self,
        command: str, # Команда для вызова. Обязательный параметр
        attachment: str = None, # Вложение
        text: str = None # Текст
        ):

        self.attachment = attachment
        self.text = text
        self.command = command

        custom_settings.update({self.command: self.__dict__})
        del custom_settings[self.command]['command']

Custom_commands(
    attachment='doc514714577_640721672',
    command='gus'
)
