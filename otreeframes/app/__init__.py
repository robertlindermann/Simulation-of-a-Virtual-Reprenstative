from otree.api import *
import openai
from dotenv import load_dotenv
import os
import base64
from groq import Groq
doc = """
Bot - Kommuniktation
"""


class C(BaseConstants):
    NAME_IN_URL = 'app'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    j=models.IntegerField(initial=1)
    character = models.StringField()
    emotion = models.StringField()
    topic = models.StringField()
    additional = models.StringField(blank=True)
    voice = models.StringField(choices=[["alloy", "Warm, männlich, leicht rau – geerdet und natürlich klingend"],
                                        ["echo", "Hell, klar, neutral – technisch und geschäftsmäßig"],
                                        ["fable", "Erzählerisch, leicht dramatisch – ideal zum Geschichtenerzählen"],
                                        ["onyx", "Tief, ruhig, eindrucksvoll – ernst und fast meditativ"],
                                        ["nova", "Hell, weiblich, freundlich – energiegeladen und lebendig"],
                                        ["shimmer", "Sanft, jung, zart – fast verspielt und fantasievoll"]])


# PAGES
class meeting(Page):
    # model = whisper.load_model("small")  # will load the model when first using for local transcription
    # j = 1
    prevchat={}
    transcript =""

    load_dotenv()
    OPENAI = os.getenv("OPENAI_API_KEY")
    
    @staticmethod
    def live_method(player, data):

        if "start" in data:
            print("started")
            return {player.id_in_group:{"status": "started trans."}}
        
         #Hier werden die eigentlichen Daten angenommen und verarbeitet.
        if "audio_data" in data:
            base64_audio = data.get('audio_data')
            # Base64 dekodieren zu Bytes
            audio_bytes = base64.b64decode(base64_audio)
            
            file_path = f"./audio.wav"
            with open(file_path, "wb") as f:    
                 f.write(audio_bytes)
            #local transcription via "small" whisper model
            client = openai.OpenAI(api_key=meeting.OPENAI)
            with open(file_path, "rb") as f:
                t = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="de"
                )
            #keeping the memory slim
            if os.path.exists(file_path):
                os.remove(file_path)
            
            #building up the whole transcript
            meeting.transcript = meeting.transcript + t.text


        if data.get("status")=="stop":
            print("stopped.")
            print(meeting.transcript)
            

            PROMPT = f"""
            Thema, welcehs Du (zum Teil) einbeziehen sollst: {player.topic}
            Charakter: Du nimmst die Rolle von {player.character} ein.
            Emotionale Haltung: Deine Antwort soll unterschwellig von {player.emotion} geprägt sein.
            Zusätzliche Informationen: Nutze {player.additional}, wenn sie zur Vertiefung des Gesprächs beitragen.

            Aufgabe:
            Antworte in einem simplen Sprachstil, wie man ihn auch in einer Unterhaltung verwendet. 
            Deine Antwort soll 2 bis 5 Sätze lang sein und soll konkret sein, ohne viel außenherumgerede. 
            Bringe nach Möglichkeit neue, inhaltlich stichhaltige Perspektiven oder wahre Tatsachen ein.

            Beachte: Wir sind in einem Gespräch, deswegen grüße mich bitte nicht erneut in jeder Nachricht, versuche aber (wenn angemessen) das Gespräch am Laufen zu halten! 
            """
   

            #Open AI communication
            client_AI = openai.OpenAI(api_key=meeting.OPENAI)

            client = Groq()
            chat_messages = []
            if player.j == 1:
                meeting.prevchat ={}
            for key, value in meeting.prevchat.items():
                role = "user" if "User" in key else "assistant"
                chat_messages.append({"role": role, "content": value})

            # Füge den aktuellen Prompt hinzu
            chat_messages.append({"role": "user", "content": meeting.transcript})


            chat_completion = client.chat.completions.create(
                messages=[
                    # Set an optional system message. This sets the behavior of the
                    # assistant and can be used to provide specific instructions for
                    # how it should behave throughout the conversation.
                    {
                        "role": "system",
                        "content": PROMPT
                    },
                   *chat_messages
                ],

                # The language model which will generate the completion.
                model="llama-3.3-70b-versatile",
                temperature= 0.6
            )

            msg = chat_completion.choices[0].message.content

            if msg.startswith('"') and msg.endswith('"'):
                msg = msg[1:-1]
            spoken_response = client_AI.audio.speech.create(
                model="tts-1-hd",
                voice=player.voice,
                input=msg
            )
            #serialize the byte data into base64 format
            ser_spoken_response = base64.b64encode(spoken_response.content).decode('utf-8')

            #Chat - Sim
            meeting.prevchat[f"User's {player.j}. message"]= meeting.transcript
            meeting.prevchat[f"BOTS's {player.j}. message"] = msg
            player.j += 1
            meeting.transcript = ""
            print(meeting.prevchat)
            return {player.id_in_group:{"status": "stopped trans.",
                                        "index":(player.j-1),
                                        "message": msg,
                                        "spoken_message": ser_spoken_response
                                        }}
class consentpage(Page):
    @staticmethod
    def live_method(player,data):
        pass       

class pregame(Page):
    form_model = "player"
    form_fields = ["character","emotion","topic","additional","voice"]
    @staticmethod
    def live_method(player,data):
        pass

class endpage(Page):
    @staticmethod
    def live_method(player,data):
        pass

page_sequence = [consentpage,pregame,meeting,endpage]
