import os
import requests
COMANDO = "!calva"

CURRENT_PATH = os.path.dirname(__file__).replace("\\", "/") + "/"
FILE_PATH = CURRENT_PATH+"besos.txt"

def command_listener(message, author, db, bot):
    if message.lower() == COMANDO:
        besos = 0
        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH, "w") as f:
                f.write("1")
                f.close()
            besos = 1
        else:
            with open(FILE_PATH, "r+") as f:
                besos = int(f.read().strip())+1
                f.seek(0)
                f.write(str(besos))
                f.truncate()
                f.close()
        bot.reproducirSonido("calva")
        bot.send_stream_message(f"{author} me ha dado un beso en la calva. Ya llevo {besos} besotes!!")
