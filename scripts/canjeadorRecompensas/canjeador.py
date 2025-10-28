import requests
from time import time
COMANDO_CANJEAR = "!canjear"
SERVER_REPRODUCCION_SONIDO = "http://192.168.1.189:5000"
SERVER_CONTROL = "http://192.168.1.188:5000"
COSTES_CANJEOS = {
    "susto" : 200,
    "destacar" : 500
}
COOLDOWN = 60 *5 # Segundos

ultimo_uso = {}


def reproducirSusto(userId, horaEjecucionComando, bot):
    global ultimo_uso
    requests.get(SERVER_REPRODUCCION_SONIDO+"/reproducirSonido?identificador=susto")
    ultimo_uso[userId] = horaEjecucionComando
    coste = COSTES_CANJEOS["susto"]
    bot.removePoints(userId, coste)
    bot.send_stream_message(userId+" ha canjeado susto por "+str(coste)+" "+bot.MONEDAS)
    

def destacarMensaje(userId, mensaje, horaEjecucionComando, bot):
    global ultimo_uso
    requests.get(SERVER_CONTROL+"/destacarMensaje?user="+userId+"&origen=youtube&mensaje="+mensaje)
    ultimo_uso[userId] = horaEjecucionComando
    coste = COSTES_CANJEOS["destacar"]
    bot.removePoints(userId, coste)
    bot.send_stream_message(userId+" ha canjeado destacar por "+str(coste)+" "+bot.MONEDAS)



def command_listener(message:str, author:str, db, bot):
    msgSplitted = message.lower().split(" ")
    if msgSplitted[0] == COMANDO_CANJEAR: # El funcionamiento es !canjear [recompensa]
        horaEjecucionComando = time()
        diferenciaCooldown = 0
        enCooldown = False
        if author in ultimo_uso.keys():
            diferenciaCooldown = horaEjecucionComando - ultimo_uso[author]
            enCooldown = diferenciaCooldown < COOLDOWN
        if msgSplitted.__len__() > 1 and (author not in ultimo_uso.keys() or not enCooldown):
            canjeo = msgSplitted[1].lower()
            puntos = bot.getPoints(author)
            if COSTES_CANJEOS.keys().__contains__(canjeo):
                if puntos >= COSTES_CANJEOS[canjeo]:
                    if canjeo == "susto":
                        reproducirSusto(author, horaEjecucionComando, bot)
                    if canjeo == "destacar" and msgSplitted.__len__() > 2:
                        destacarMensaje(author, message.replace(COMANDO_CANJEAR, "").replace("destacar", "").strip(), horaEjecucionComando, bot)
                else:
                    bot.send_stream_message(author+", necesitas "+ str(COSTES_CANJEOS[canjeo])+" "+bot.MONEDAS+" para canjearlo, y tienes "+str(puntos))
        if enCooldown:
            bot.send_stream_message("Espera "+str(int(COOLDOWN-round(diferenciaCooldown)))+" segundos antes de volver a canjear una recompensa")