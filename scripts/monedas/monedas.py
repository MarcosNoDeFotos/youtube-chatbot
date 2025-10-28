
COMANDO = "!monedas"

def command_listener(message:str, author:str, db, bot):
    if message == COMANDO:
        bot.send_stream_message(f"{author} tienes {bot.getPoints(author)} {bot.MONEDAS}")