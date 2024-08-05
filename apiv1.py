from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.tts import AzureTextToSpeech
from utils.chatengine import ChatEngine
from pydantic import BaseModel
from functions.checkin import CheckinHandler
from loguru import logger
from utils.a2f_ac import Controller
from typing import Optional

EMOTION_LIST = {
    "amazement": 0,
    "anger": 0,
    "cheekiness": 0,
    "disgust": 0,
    "fear": 0,
    "grief": 0,
    "joy": 0,
    "outofbreath": 0,
    "pain": 0,
    "sadness": 0
}

suplementary_emotion_vals = {
    "st_a2e_multiplier": 0.5,
    "st_external_multiplier": 0.5,
    "st_max_emotion_change": 0.08,
}

class Msg(BaseModel):
    content: str
    language: str
    gesture: Optional[str] = None

class CheckinInterface(BaseModel):
    host_email: str
    visitor_name: str   

class AnimationData(BaseModel):
    name: str

app = FastAPI()

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


a2f_controller = Controller()
init_convesation = [{"role": "system", "content": "You are Elisa reception agent that can handle visitor checkin and answer all information related to Elisa Oyj. Elisa Oyj is a telecommunications, ICT and online service company operating in Finland. Keep your answers short and on point."},]
chatEngine = ChatEngine(init_convesation)
tts = AzureTextToSpeech()
checkin_handler = CheckinHandler()

@app.get("/")
def read_root():    
    return {"Hello": "World"}


@app.get("/checkin/host_data")
def get_host_data():
    host_data = checkin_handler.get_host_list()
    return host_data 

@app.post("/checkin/inform_host")
def inform_host(checkinInterface: CheckinInterface):
    a2f_controller.push_gesture("Phone_Dialing")
    checkin_handler.inform_host(checkinInterface.host_email, checkinInterface.visitor_name)
    return "email sent"

@app.post("/streams/add_stream")
def add_stream():
    a2f_controller.add_stream()
    return

@app.post("/streams/remove_stream")
def remove_stream():
    a2f_controller.remove_stream()
    return 

@app.post("/send/posture")
def send_posture(animationData: AnimationData):
    a2f_controller.push_posture(animationData.name)
    return

@app.post("/send/gesture")
def send_posture(animationData: AnimationData):
    a2f_controller.push_gesture(animationData.name)
    return

@app.post("/send/user_message")
async def send_user_message(userMsg: Msg):
    try:
        a2f_controller.push_posture("Thinking")
        user_input = userMsg.content    
        message = {"role": "user", "content": user_input}
        response_text = chatEngine.create(message)

        tts.speech(response_text, language=userMsg.language)
        a2f_controller.push_posture("Talking")
        audiopath = "./response.wav"
        await a2f_controller.push_audio(audiopath)
        a2f_controller.push_posture("Listening")
        return {'user_input': user_input, 'response_text': response_text}   
    except:
        return {'user_input': user_input, 'response_text': '500'}

@app.post("/send/ai_message")
async def send_ai_message(aiMsg: Msg):
    try:
        tts.speech(aiMsg.content, language=aiMsg.language)
        audiopath = "./response.wav"
        if aiMsg.gesture:
            a2f_controller.push_gesture(aiMsg.gesture)
        else:
            a2f_controller.push_posture("Talking")
        audiopath = "./response.wav"
        await a2f_controller.push_audio(audiopath)
        a2f_controller.push_posture("Listening")
        return {'status': "Ready", 'response_text': aiMsg.content}   
    except:
        return {'status': "Ready", 'response_text': '500'}
    
@app.post("/emotion_state")
def set_emotion_state():
    ## TODO: ver2
    return

@app.get("/emotion_state")
def get_emotion_state():
    ## TODO: ver2
    return  