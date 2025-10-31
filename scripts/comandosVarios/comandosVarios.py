
COMANDOS = {
    "!redes": "Youtube: https://www.youtube.com/@marcosnodefotos | TikTok: https://tiktok.com/@marcosnodefotos | Kick: https://kick.com/marcosnodefotos | Instagram: https://instagram.com/marcosnodefotos",
    "!pc": "Pc Gaming: https://es.pc-builder.io/builds/D5CNOrHv | PC Streaming: https://es.pc-builder.io/builds/i6iKN0kj",
    "!donar": "¿Quieres ayudarme? Te lo agradezco mucho!! Visita este enlace https://streamlabs.com/marcosnodefotos o hazlo por PayPal (https://paypal.me/marcosspg)",
    "!discord": "Entra en mi discord y entérate de novedades y demás. Te espero allí!! https://discord.gg/e427a5r",
    "!comandos": "!redes, !pc, !donar, !discord, !calva, !gamble",
}

def command_listener(message, author, db, bot):
    if message.lower() in COMANDOS.keys():
        bot.send_stream_message(COMANDOS[message.lower()])