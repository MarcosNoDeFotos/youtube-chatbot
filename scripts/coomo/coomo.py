import os
import requests
COMANDOS = ["!coomo", "!como"]


def command_listener(message, author, db, bot):
    if message.lower() in COMANDOS:
        bot.reproducirSonido("coomo")
