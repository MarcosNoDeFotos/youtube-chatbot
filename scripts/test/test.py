def command_listener(message, author, db, bot):
    if message.lower() == "!ping":
        bot.send_stream_message(f"🏓 Pong, {author}!")