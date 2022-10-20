class Custom_commands:
    def __init__(self,
        command: str, # Команда для вызова. Обязательный параметр

        attachment: str = None, # Вложение
        text: str = None # Текст
        ):

        self.attachment = attachment
        self.text = text

        custom_settings.update({command: self.__dict__})

custom_settings = {}
