import os
import requests
COMANDO = "!coomo"


def command_listener(message, author, db, bot):
    if message.lower() == COMANDO:
        bot.reproducirSonido("coomo")
