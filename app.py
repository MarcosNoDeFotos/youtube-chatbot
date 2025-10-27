import pytchat
import importlib
import pickle
import os
import time
import sqlite3
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import threading
import traceback

class YouTubeChatBot:
    youtube = None
    live_chat_id = None
    points_db = None
    scripts = []
    listener_active = True

    # ==============================
    # CONFIGURACIÓN
    # ==============================
    VIDEO_ID = "UzHCjHecqDc"  # El ID del stream
    TOKEN_FILE = "token_bot.pickle"  # Credenciales OAuth de la cuenta del bot
    DB_PATH = "userPoints.db"



    # =========================================================
    # AUTENTICACIÓN CON LA CUENTA DEL BOT
    # =========================================================
    @staticmethod
    def get_authenticated_service():
        SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        creds = None
        if os.path.exists("token_bot.pickle"):
            with open("token_bot.pickle", "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token_bot.pickle", "wb") as token:
                pickle.dump(creds, token)
        return build("youtube", "v3", credentials=creds)

    @staticmethod
    def get_stream_live_id():
        SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
        input("Inicia sesión con la cuenta de YouTube en la que se inicia el stream para sacar el Live Chat ID (pulsa intro)")
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
        youtube = build("youtube", "v3", credentials=creds)

        request = youtube.liveBroadcasts().list(
            part="snippet",
            broadcastStatus="active",
            broadcastType="all"
        )
        response = request.execute()
        return response["items"][0]["snippet"]["liveChatId"]


    # ==============================
    # INICIALIZACIÓN
    # ==============================
    @staticmethod
    def start():
        print("🚀 Iniciando YouTubeChatBot...")
        with sqlite3.connect(YouTubeChatBot.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS points (
                    username TEXT PRIMARY KEY,
                    points INTEGER DEFAULT 0
                )
            """)
            conn.commit()

        # Autenticarse con la cuenta del bot (ya autorizada previamente)
        
        YouTubeChatBot.youtube = YouTubeChatBot.get_authenticated_service()

        # Obtener el liveChatId del stream
        YouTubeChatBot.live_chat_id = YouTubeChatBot.get_stream_live_id()
        # YouTubeChatBot.live_chat_id = "KicKGFVDaTRwa0dfT2hfRUU1N3R3VVRMLXhIURILQUJTRmJNdjl3RnM"
        print(f"✅ Conectado al chat ID: {YouTubeChatBot.live_chat_id}")

        # Cargar scripts
        YouTubeChatBot.load_scripts()

        # Iniciar el listener del chat
        # YouTubeChatBot.listen_chat()
        YouTubeChatBot.listen_chat()



    # ==============================
    # CARGAR SCRIPTS
    # ==============================
    @staticmethod
    def load_scripts():
        scripts_dir = "scripts"
        YouTubeChatBot.scripts = []

        for filename in os.listdir(scripts_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"{scripts_dir}.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, "command_listener"):
                        YouTubeChatBot.scripts.append(module)
                        print(f"✅ Script cargado: {filename}")
                except Exception as e:
                    print(f"⚠️ Error cargando {filename}: {e}")

    # ==============================
    # ESCUCHAR CHAT
    # ==============================
    @staticmethod
    def listen_chat():
        chat = pytchat.create(video_id=YouTubeChatBot.VIDEO_ID)
        print("🤖 Escuchando mensajes en el chat...")

        while chat.is_alive() and YouTubeChatBot.listener_active:
            for c in chat.get().sync_items():
                author = c.author.name
                message = c.message.strip()

                print(f"[{author}] {message}")

                # Llamar a todos los scripts
                for script in YouTubeChatBot.scripts:
                    try:
                        script.command_listener(message, author, YouTubeChatBot.points_db, YouTubeChatBot)
                    except Exception as e:
                        print(f"⚠️ Error en {script.__name__}: {e}")

            time.sleep(0.2)

    # ==============================
    # ENVIAR MENSAJE AL CHAT
    # ==============================
    @staticmethod
    def send_stream_message(text):
        if not YouTubeChatBot.youtube or not YouTubeChatBot.live_chat_id:
            print("❌ El bot no está conectado al chat aún.")
            return

        try:
            YouTubeChatBot.youtube.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": YouTubeChatBot.live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {"messageText": text}
                    }
                }
            ).execute()
            print(f"[BOT] {text}")
        except Exception as e:
            print(f"⚠️ Error enviando mensaje: {e}")

    @staticmethod
    def addPoints(user, amount):
        with sqlite3.connect(YouTubeChatBot.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO points (username, points) VALUES (?, 0)", (user,))
            cursor.execute("UPDATE points SET points = points + ? WHERE username = ?", (amount, user))
            conn.commit()
    @staticmethod
    def removePoints(user, amount):
        with sqlite3.connect(YouTubeChatBot.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE points SET points = points - ? WHERE username = ?", (amount, user))
            conn.commit()
    @staticmethod
    def getPoints(user):
        with sqlite3.connect(YouTubeChatBot.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM points WHERE username = ?", (user,))
            row = cursor.fetchone()
            return row[0] if row else 0


    @staticmethod
    def stop():
        print("Parando...")
        YouTubeChatBot.listener_active = False

    # ==============================
    # CONSOLA INTERACTIVA
    # ==============================
    @staticmethod
    def console_loop():
        """
        Lanza una consola de comandos en un hilo aparte.
        Permite ejecutar código dinámico con exec() en tiempo real.
        """
        time.sleep(5)
        print("🖥️ Consola lista. Escribe código Python (o 'exit' para salir).")
        while True:
            try:
                cmd = input(">>> ").replace("Bot.", "YouTubeChatBot.")
                if cmd.strip().lower() in ("exit", "quit"):
                    break
                if not cmd.strip():
                    continue

                # Ejecutar el comando en el contexto global del bot
                try:
                    result = eval(cmd, globals(), locals())
                    if result is not None:
                        print(result)
                except SyntaxError:
                    exec(cmd, globals(), locals())
                except Exception:
                    traceback.print_exc()

            except (EOFError, KeyboardInterrupt):
                break
if __name__ == "__main__":
    # Iniciar la consola en un hilo separado
    console_thread = threading.Thread(target=YouTubeChatBot.console_loop, daemon=True)
    console_thread.start()

    # Ejecutar el bot en el hilo principal (pytchat necesita esto)
    YouTubeChatBot.start()
