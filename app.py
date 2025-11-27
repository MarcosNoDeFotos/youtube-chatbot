import pytchat
import importlib
import pickle
import os
import sys
import requests
import time
import json
import sqlite3
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
import threading
import traceback

CURRENT_PATH = os.path.dirname(__file__).replace("\\", "/") + "/"

class YouTubeChatBot:
    MONEDA = "Moneda Calva"
    MONEDAS = "Monedas Calvas"
    RECOMPENSA_CADA_X_MINUTOS = 5
    RECOMPENSA_AUTOMATICA = 20
    BOT_NAME = "lord_shit_mndf"
    SERVER_REPRODUCCION_SONIDO = "http://192.168.1.189:5000"
    youtube = None
    live_chat_id = None
    video_id = None  # El ID del stream
    points_db = None
    scripts = []
    listener_active = True
    users_last_message_time = {}
    app_ready = False
    autor_ultimo_mensaje = None
    # ==============================
    # CONFIGURACIÓN
    # ==============================
    TOKEN_FILE = "token_bot.pickle"  # Credenciales OAuth de la cuenta del bot
    DB_PATH = "userPoints.db"



    # =========================================================
    # AUTENTICACIÓN CON LA CUENTA DEL BOT
    # =========================================================
    @staticmethod
    def get_authenticated_service():
        SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        creds = None

        # Cargar si existe
        if os.path.exists("token_bot.pickle"):
            with open("token_bot.pickle", "rb") as token:
                creds = pickle.load(token)

        # Si no es válida → reautenticar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print("⚠️ Error refrescando token, regenerando autorización…", e)
                    creds = None

            # Si no se pudo refrescar → pedir login
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json",
                    SCOPES
                )
                creds = flow.run_local_server(
                    port=0,
                    access_type="offline",
                    prompt="consent"
                )

            # Guardar token nuevo
            with open("token_bot.pickle", "wb") as token:
                pickle.dump(creds, token)

        return build("youtube", "v3", credentials=creds)

    @staticmethod
    def get_stream_live_id():
        SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
        creds = None

        # 1. Cargar credenciales si existen
        if os.path.exists("live_credentials.pickle"):
            with open("live_credentials.pickle", "rb") as token:
                creds = pickle.load(token)

        # 2. Si no existen o no son válidas → pedir autenticación
        if not creds or not creds.valid:
            input("Inicia sesión con la cuenta de YouTube en la que se inicia el stream para sacar el Live Chat ID (pulsa intro)")
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    # Refresh falló → pedir login otra vez
                    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
                    creds = flow.run_local_server(port=0)
            else:
                # No hay refresh token → login obligatorio
                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
                creds = flow.run_local_server(port=0)

            # Guardar las credenciales para futuras ejecuciones
            with open("live_credentials.pickle", "wb") as token:
                pickle.dump(creds, token)

        # 3. Crear el servicio
        youtube = build("youtube", "v3", credentials=creds)

        # 4. Consultar el directo activo
        request = youtube.liveBroadcasts().list(
            part="snippet",
            broadcastStatus="active",
            broadcastType="all"
        )
        response = request.execute()

        return response["items"][0]["snippet"]["liveChatId"], response["items"][0]["id"]



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
        live_chat_id, video_id = YouTubeChatBot.get_stream_live_id()
        YouTubeChatBot.live_chat_id = live_chat_id
        YouTubeChatBot.video_id = video_id
        # YouTubeChatBot.live_chat_id = "KicKGFVDaTRwa0dfT2hfRUU1N3R3VVRMLXhIURILQUJTRmJNdjl3RnM"
        print(f"✅ Conectado al Stream ID: {YouTubeChatBot.video_id}")
        print(f"✅ Conectado al chat ID: {YouTubeChatBot.live_chat_id}")

        # Cargar scripts
        YouTubeChatBot.load_scripts()

        # Iniciar el listener del chat
        # YouTubeChatBot.listen_chat()
        YouTubeChatBot.app_ready = True
        YouTubeChatBot.listen_chat()



    # ==============================
    # CARGAR SCRIPTS
    # ==============================
    @staticmethod
    def load_scripts():
        scripts_dir = "scripts/"
        YouTubeChatBot.scripts = []

        for scriptname in os.listdir(scripts_dir): # /scripts
            if os.path.isdir(scripts_dir+scriptname) and scriptname != "__pycache__":
                for filename in os.listdir(scripts_dir+scriptname): # /scripts/[nombre script]
                    if filename.endswith(".py") and filename != "__init__.py": # /scripts/[nombre script]/[nombre].py
                        module_name = f"{scripts_dir[:-1]}.{scriptname}.{filename[:-3]}"
                        try:
                            if module_name in sys.modules:
                                module = sys.modules[module_name]
                                importlib.reload(module)
                                print(f"♻️ Script recargado: {filename}")
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
        while YouTubeChatBot.listener_active:
            try:
                print("🤖 Escuchando mensajes en el chat...")
                chat = pytchat.create(video_id=YouTubeChatBot.video_id)
                while chat.is_alive() and YouTubeChatBot.listener_active:
                    for c in chat.get().sync_items():
                        author = str(c.author.name)
                        message = c.message.strip()
                        YouTubeChatBot.autor_ultimo_mensaje = author
                        # print(f"[{author}] {message}")
                        if not author.__contains__(YouTubeChatBot.BOT_NAME.replace("@", "")):
                            YouTubeChatBot.users_last_message_time[author] = time.time()
                            # Llamar a todos los scripts
                            for script in YouTubeChatBot.scripts:
                                try:
                                    script.command_listener(message, author, YouTubeChatBot.points_db, YouTubeChatBot)
                                except Exception as e:
                                    print(f"⚠️ Error en {script.__name__}: {e}")
                    time.sleep(0.2)
            except Exception as e:
                print(f"💥 Error en pytchat: {e}")
                print("🔁 Reiniciando conexión en 10 segundos...")
                time.sleep(10)
    # ==============================
    # REPARTIR PUNTOS CADA 5 MINUTOS
    # ==============================
    @staticmethod
    def reward_active_users():
        print(F"🎯 Sistema de recompensas iniciado (cada {YouTubeChatBot.RECOMPENSA_CADA_X_MINUTOS} minutos).")
        lastMinuteRewarded = 0
        while YouTubeChatBot.listener_active:
            now = datetime.now()
            minute = now.minute

            # Si estamos justo en un múltiplo de 5 minutos (00, 05, 10, 15...)
            if minute % 5 == 0 and lastMinuteRewarded != minute:
                lastMinuteRewarded = minute
                cutoff_time = time.time() - 5 * 60  # Hace 5 minutos
                rewarded_users = []

                for user, last_msg_time in list(YouTubeChatBot.users_last_message_time.items()):
                    if last_msg_time >= cutoff_time:
                        YouTubeChatBot.addPoints(user, 20)
                        rewarded_users.append(user)

                if rewarded_users:
                    print(f"{now.hour}:{now.minute} Recompensados {len(rewarded_users)} usuarios activos ({', '.join(rewarded_users)}).")
                    try:
                        YouTubeChatBot.send_stream_message(F"🎁 ¡{YouTubeChatBot.RECOMPENSA_AUTOMATICA} {YouTubeChatBot.MONEDAS} para los usuarios activos del chat!")
                    except Exception:
                        pass
                else:
                    print(f"{now.hour}:{now.minute} No hay usuarios activos en los últimos 5 minutos.")

            # Esperar 10 segundos y volver a verificar
            time.sleep(10)

    # ==============================
    # MENSAJES AUTOMÁTICOS DEL BOT EN EL CHAT
    # ==============================
    @staticmethod
    def mensajes_automaticos(mensaje:str, segundos_cooldown:float):
        print(F"🚩 Mensaje automático \"{mensaje[0:25]}...\" cada {segundos_cooldown}s")
        while YouTubeChatBot.listener_active:
            time.sleep(segundos_cooldown)
            #Si alguien ha enviado un mensaje y no ha sido el bot el último que ha enviado un mensaje
            if YouTubeChatBot.autor_ultimo_mensaje and not YouTubeChatBot.autor_ultimo_mensaje.__contains__(YouTubeChatBot.BOT_NAME.replace("@", "")):
                YouTubeChatBot.send_stream_message(mensaje)
                # print(mensaje)


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
    def reproducirSonido(sonido):
        requests.get(YouTubeChatBot.SERVER_REPRODUCCION_SONIDO+"/reproducirSonido?identificador="+sonido)
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
        while not YouTubeChatBot.app_ready:
            time.sleep(5)
        time.sleep(2)
        print("🖥️ Consola lista ('Bot.stop()' para salir).")
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
    threading.Thread(target=YouTubeChatBot.console_loop, daemon=True).start()
    threading.Thread(target=YouTubeChatBot.reward_active_users, daemon=True).start()

    #Mensajes automáticos enviados por el bot
    mensajesAutomaticosPath = CURRENT_PATH+"mensajes_automaticos.json"
    if os.path.exists(mensajesAutomaticosPath):
        with open(mensajesAutomaticosPath, encoding="utf-8") as mensajesAutomaticosFile:
            mensajesAutomaticos = json.load(mensajesAutomaticosFile)
            for mensaje in mensajesAutomaticos:
                threading.Thread(target=YouTubeChatBot.mensajes_automaticos, args=(mensaje["mensaje"], float(mensaje["cooldown_segundos_envio"])), daemon=True).start()
    else:
        print(f"⚠️ No existe el fichero {mensajesAutomaticosPath}. No se enviarán mensajes automáticos")

    # Ejecutar el bot en el hilo principal (pytchat necesita esto)
    YouTubeChatBot.start()
