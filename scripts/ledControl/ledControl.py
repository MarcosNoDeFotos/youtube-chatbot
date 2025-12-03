import requests
from time import time
COMANDOS = ["!led", "!leds"]
COOLDOWN = 5*60 #Segundos
# COOLDOWN = 2 #Segundos
RGB_ENDPOINT_COLOR = "http://192.168.1.189:5000/rgb_establecerColor"

lastTimeExecuted = 0

coloresValidos = {
    "azul": "17,0,255",
    "rojo": "255,0,0",
    "verde": "0,255,0",
    "morado": "168,0,146",
    "amarillo" : "214,179",
    "furcia": "230,0,111",
    "blanco": "255,255,255",
    "apagado": "0,0,0",
}

efectosValidos = [
    "static",
    "loop",
    "vuelta",
    "fill",
    "random",
    "destello",
]


def enviarColor(color, efecto):
    requests.post(RGB_ENDPOINT_COLOR, data={"color": color, "animacion": efecto})

def command_listener(message:str, author:str, db, bot):
    global lastTimeExecuted
    msgSplitted = message.lower().split(" ")
    if msgSplitted[0] in COMANDOS:
        if msgSplitted.__len__() == 1 or (msgSplitted.__len__() == 2 and msgSplitted[1] == "help"):
            bot.send_stream_message(f"!leds [color] [efecto]: ¡Cambia el color de mi gorro! Efectos válidos: {', '.join(efectosValidos)}. Ejemplo: !leds rojo random")
        if msgSplitted.__len__() >= 2:
            color = msgSplitted[1]
            efecto = "loop"
            if msgSplitted.__len__() >= 3:
                if msgSplitted[2] in efectosValidos:
                    efecto = msgSplitted[2]
            if str(color).strip() == "reset" and author.lower().replace("@", "") == bot.STREAMER_NAME.lower():
                lastTimeExecuted = 0
                bot.send_stream_message(f"👌")
            elif str(color).strip()!="help":
                if lastTimeExecuted == 0 or time()-lastTimeExecuted >= COOLDOWN:
                    lastTimeExecuted = time()
                    if color in coloresValidos.keys():
                        enviarColor(coloresValidos[color], efecto); 
                        bot.send_stream_message(author+" ha cambiado el color de mi gorro!!!")
                    if color == "multicolor":
                        enviarColor("", "multicolor")
                        bot.send_stream_message(author+" ha cambiado el color de mi gorro!!!")
                else:
                    bot.send_stream_message(f"Que me vas a fundir las luces!! Espérate un ratico ({int(COOLDOWN-(time()-lastTimeExecuted))}s)")
