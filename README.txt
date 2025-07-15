Thank you for trying out the Otree program or perhaps developing it further.
To start it, you have to add some codes/keys (see below), but then you only need to start the program as a classic Otree Project/app.

Quick introduction:
- navigate to the __init__.py
- open console/terminal
- for local devserver, type in: otree devserver
- then open the address in your favorite browser:http://localhost:8000
- you can also start this project on a glba Server, see several tutorials on the internet

For set-up you Need to add:
- SECRET_KEY in Settings.py
- OPENAI_API_KEY in .env (for tts-1-hd and whisper-1)
- GROQ_API_KEY in .env (for llama-3.3-70b-versatile)
- Jitsi API key in meeting.html in line 165
- Jitsi Sever Domain in meeting.html in line 167
- Menti-Survey-QR-Code in endpage.html in line 86