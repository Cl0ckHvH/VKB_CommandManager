################ Функции для настройки конфига ######################################################################

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
