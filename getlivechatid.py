from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0)
youtube = build("youtube", "v3", credentials=creds)

request = youtube.liveBroadcasts().list(
    part="snippet",
    broadcastStatus="active",
    broadcastType="all"
)
response = request.execute()

print("✅ liveChatId:", response["items"][0]["snippet"]["liveChatId"])
