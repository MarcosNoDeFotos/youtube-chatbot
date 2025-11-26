import requests
from time import time, sleep
COMANDOS = ["!led", "!leds"]
COOLDOWN = 5*60 #Segundos
# COOLDOWN = 2 #Segundos
RGB_ENDPOINT_COLOR = "http://192.168.1.189:5000/rgb_establecerColor"
RGB_ENDPOINT_ANIMACION = "http://192.168.1.189:5000/rgb_establecerAnimacion"

lastTimeExecuted = 0

coloresValidos = {
    "azul": "17,0,255",
    "rojo": "255,0,0",
    "verde": "0,255,0",
    "morado": "168,0,146",
    "amarillo" : "214,179",
    "furcia": "230,0,111",
    "rainbow": "0,0,0",
    "blanco": "255,255,255",
    "apagado": "0,0,0",
}

efectosValidos = [
    "static",
    "loop"
]

def enviarColor(color, efecto):
    requests.post(RGB_ENDPOINT_COLOR, data={"color": color})
    sleep(2)
    requests.post(RGB_ENDPOINT_ANIMACION, data={"animacion": efecto})

def command_listener(message:str, author:str, db, bot):
    global lastTimeExecuted
    msgSplitted = message.lower().split(" ")
    if msgSplitted[0].lower() in COMANDOS:
        if msgSplitted.__len__() >= 2:
            color = msgSplitted[1]
            efecto = "loop"
            if str(color).strip()!="help":
                if lastTimeExecuted == 0 or time()-lastTimeExecuted >= COOLDOWN:
                    lastTimeExecuted = time()
                    colorEsHexa = True
                    try:
                        int(color[1:], 16);
                    except:
                        colorEsHexa = False
                    if color in coloresValidos.keys():
                        if color == "rainbow":
                            enviarColor("0,0,0", "rgbLoco"); 
                        else:
                            enviarColor(coloresValidos[color], efecto); 
                        bot.send_stream_message(author+" ha cambiado el color de mi gorro!!!")
                    # elif (str(color).__len__()==7 and str(color)[0:1] == "#" and colorEsHexa):
                    #     enviarColor(coloresValidos[color]); 
                    #     bot.send_stream_message(author+" ha cambiado el color de mi gorro!!!")

                else:
                    bot.send_stream_message(f"Que me vas a fundir las luces!! Espérate un ratico ({int(COOLDOWN-(time()-lastTimeExecuted))}s)")
            else:
                bot.send_stream_message(f"!leds [color]: ¡Usa este comando para cambiar el color de mi gorro! Colores disponibles: {', '.join(coloresValidos.keys())}")
