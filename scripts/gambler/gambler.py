import random
import time



COMANDOS = ["!gamble", "!apuesta", "!gmb"]
COOLDOWN = 5*60 # Segundos

slots = ["❤️", "😎", "⭐", "👽"]

ultimo_uso = {}


def command_listener(message:str, author:str, db, bot):
    msgSplitted = message.lower().split(" ")
    if msgSplitted[0] in COMANDOS:
        if msgSplitted.__len__() == 1 or (msgSplitted.__len__() > 1 and msgSplitted[1] in ["help", "?", "ayuda"]): # Si usa !gamble (sin nada más) o !gamble help
            bot.send_stream_message("Usa !gamble [cantidad]: Apuesta tus "+bot.MONEDAS+" en la tragaperras 🎰. 3 ⭐ = x2.5. 3 emojis iguales = x2. 2 emojis iguales = x1.5. Para consultar tus "+bot.MONEDAS+", usa !monedas")
        else:
            try:
                apuesta = int(msgSplitted[1])
                horaEjecucionComando = time.time()
                puntos = bot.getPoints(author)
                if apuesta > 0:
                    diferenciaCooldown = 0
                    enCooldown = False
                    if author in ultimo_uso.keys():
                        diferenciaCooldown = horaEjecucionComando - ultimo_uso[author]
                        enCooldown = diferenciaCooldown < COOLDOWN
                    if apuesta <=puntos and (author not in ultimo_uso.keys() or not enCooldown):
                        #r = [random.choice(slots) for _ in range(3)] # Random no válido para python 2.7. Siempre saca los 2 primeros valores de la lista slots
                        r = []
                        for _ in range(3):
                            random.shuffle(slots)  # desordena aleatoriamente la lista
                            r.append(slots[0])
                        resultado = "".join(r)
                        multiplicador = 0
                        msg = author+" ha apostado "+str(apuesta)+" " + bot.MONEDAS + ". El resultado es ["+resultado+"]. "
                        if r == ["⭐","⭐","⭐"]:
                            multiplicador = 2.5
                            msg += "Apuesta güena güena 😍😍!!"
                        elif r[0] == r[1] and r[0] == r[2]:
                            multiplicador = 2
                            msg += "Olee!! 😘"
                        elif r[0] == r[1] or r[0] == r[2] or r[1] == r[2]:
                            multiplicador = 1.5
                            msg += "Algo es algo... 🤷‍♂️"
                        else:
                            multiplicador = 1
                            msg += "Menudo mojón xd 💩💩"
                        ganancia = int(round(apuesta * multiplicador)) - apuesta  # Ejemplo fijo
                        if multiplicador != 1:
                            bot.addPoints(author, ganancia)
                        else:
                            bot.removePoints(author, apuesta)
                            ganancia = -apuesta;
                        bot.send_stream_message(msg+ ". Ahora tiene "+ str(puntos+ganancia) + " " + bot.MONEDAS + "🪙")
                        ultimo_uso[author] = horaEjecucionComando
                    elif enCooldown:
                        bot.send_stream_message("Espera "+str(int(COOLDOWN-round(diferenciaCooldown)))+" segundos antes de volver a apostar")
                    else:
                        bot.send_stream_message("No puedes apostar más "+bot.MONEDAS+ " de las que tienes")
            except:
                None