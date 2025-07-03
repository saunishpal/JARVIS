import azure.cognitiveservices.speech as speechsdk
import webbrowser
import pyttsx3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import openai
import random
import os
import platform
import requests
from datetime import datetime

app = FastAPI()

# Azure Speech Configuration
speech_key =   # Replace with your actual Azure Speech API key
service_region = "centralindia"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "en-AU-WilliamNeural"  # Male voice

# OpenAI API key setup
openai.api_key =  # Replace with your actual OpenAI API key

# Pyttsx3 fallback voice synthesis
engine = pyttsx3.init()

# Weather API key setup (using OpenWeatherMap)
weather_api_key = # Replace with your OpenWeatherMap API key
weather_city = "KOLKATA"  # Specify your city here

# Path to the wake word model
keyword_model_path = ()  # Replace with the path to your keyword model

# Load the wake word model
keyword_model = speechsdk.KeywordRecognitionModel(keyword_model_path)

# Greeting commands
greetings = [
    "Hello Sir, I am Jarvis. How may I assist you today?",
    "Good day, Sir. What can I do for you?",
    "Welcome back, Sir. How can I help?",
    "At your service, Sir. What do you need today?",
    "Greetings Sir, ready for your command."
]

# Function to get weather info
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={weather_city}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    weather_data = response.json()

    if response.status_code == 200:
        main_weather = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        return f"The current weather in {weather_city} is {main_weather} with a temperature of {temp}°C."
    else:
        return "Sorry, I couldn't fetch the weather information."

# Function to get the current greeting based on time
def get_time_based_greeting():
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        return "Good morning, Sir."
    elif 12 <= current_hour < 17:
        return "Good afternoon, Sir."
    elif 17 <= current_hour < 21:
        return "Good evening, Sir."
    else:
        return "Good night, Sir."

# Function to speak with Azure TTS
def speak(text):
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    synthesizer.speak_text_async(text)

# Function to process AI response
def ai_process(command):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Jarvis, a virtual assistant."},
            {"role": "user", "content": command}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Function to process commands
def process_command(command):
    command = command.lower()
    
    if "open google" in command:
        webbrowser.open("https://google.com")
        response_text = "Opening Google"
    elif "open facebook" in command:
        webbrowser.open("https://facebook.com")
        response_text = "Opening Facebook"
    elif "open youtube" in command:
        webbrowser.open("https://youtube.com")
        response_text = "Opening YouTube"
    elif "search google for" in command or "google" in command:
        search_query = command.replace("search google for", "").replace("google", "").strip()
        if search_query:
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
            response_text = f"Searching Google for {search_query}"
        else:
            response_text = "Please provide a search term."
    elif "search youtube for" in command or "youtube" in command:
        search_query = command.replace("search youtube for", "").replace("youtube", "").strip()
        if search_query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
            response_text = f"Searching YouTube for {search_query}"
        else:
            response_text = "Please provide a search term."
    
    # Automate browser commands
    elif "close all tabs" in command or "close browser" in command:
        if platform.system() == "Windows":
            os.system("taskkill /IM chrome.exe /F")  # For Chrome on Windows
            response_text = "Closing all browser tabs"
        elif platform.system() == "Darwin":
            os.system("osascript -e 'tell application \"Google Chrome\" to close every window'")  # For MacOS
            response_text = "Closing all browser tabs"
        elif platform.system() == "Linux":
            os.system("pkill chrome")  # For Linux
            response_text = "Closing all browser tabs"
    
    elif "play music" in command:
        webbrowser.open("https://spotify.com")
        response_text = "Opening Spotify"
    
    # Automate file management or system commands
    elif "create new folder" in command:
        folder_name = command.replace("create new folder", "").strip()
        if folder_name:
            os.makedirs(folder_name, exist_ok=True)
            response_text = f"Created new folder: {folder_name}"
        else:
            response_text = "Please specify a folder name."




      # Handle computer automation commands
    elif "shutdown the computer" in command or "shut down the computer" in command:
        response_text = "Shutting down the computer"
        speak(response_text)
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        elif platform.system() == "Linux" or platform.system() == "Darwin":
            os.system("sudo shutdown now")
    
    elif "restart the computer" in command:
        response_text = "Restarting the computer"
        speak(response_text)
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")
        elif platform.system() == "Linux" or platform.system() == "Darwin":
            os.system("sudo reboot")        
    
 
    
    elif any(greeting.lower() in command for greeting in greetings):
        response_text = random.choice(greetings)
    
    elif "stop jarvis" in command:
        response_text = "As you wish, sir."
        speak(response_text)
        return "stop"  # Signal to stop
    
    else:
        response_text = ai_process(command)
    
    speak(response_text)
    return response_text

# Function to listen for commands after wake word
def listen_for_commands():
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    print("Listening for command...")
    result = recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {result.text}")
        return result.text
    else:
        print("Command not recognized")
        return None

# Function to recognize the wake word
def recognize_wake_word():
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    keyword_recognizer = speechsdk.KeywordRecognizer(audio_config=audio_config)

    def recognized_callback(evt):
        print(f"Wake word recognized: {evt.result.text}")
        speak("Yes, sir.")
        return True  # Indicate the wake word was recognized

    keyword_recognizer.recognized.connect(recognized_callback)
    return keyword_recognizer.recognize_once_async(model=keyword_model).get()

# WebSocket Communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # Initial greeting based on time and weather
        time_greeting = get_time_based_greeting()
        weather_info = get_weather()
        initial_greeting = f"{time_greeting} {weather_info}"

        speak(initial_greeting)
        await websocket.send_text(initial_greeting)

        while True:
            # Start wake word detection
            wake_word_result = recognize_wake_word()

            # Proceed only if wake word is recognized
            if wake_word_result.reason == speechsdk.ResultReason.RecognizedKeyword:
                await websocket.send_text("Wake word 'JARVIS' recognized.")
                speak("Yes, sir.")

                # Listen for command after wake word
                command = listen_for_commands()
                if command:
                    response = process_command(command)
                    await websocket.send_text(f"JARVIS: {response}")
                else:
                    await websocket.send_text("Command not recognized, please try again.")

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

