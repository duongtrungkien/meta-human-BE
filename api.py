from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.tts import AzureTextToSpeech
from utils.chatengine import ChatEngine
from contextlib import asynccontextmanager
from pydantic import BaseModel
from functions.checkin import CheckinHandler
from loguru import logger
import threading

class Msg(BaseModel):
    content: str   

class CheckinInterface(BaseModel):
    host_email: str
    visitor_name: str


async def establish_connection_ac():
    ip = "127.0.0.1"
    port = "52000"
    def handle_crash(msg):
        print(msg)
    res, msg = core_func.start_connection_ac(ip, port, handle_crash)
    return {"res": res, "msg": msg}

async def establish_connection_renderer():
    ip="127.0.0.1"
    port_audio="8021"
    port_blendshape="8021"
    avatar_model="Audio2Face"
    def handle_crash(msg):
        print(msg)
    res, msg = core_func.start_connection_renderer(ip, port_audio, port_blendshape, avatar_model, handle_crash)
    return {"res": res, "msg": msg}

def disconnect_renderer():
    if core_func.is_streaming():
        core_func.stop_connection_renderer()
    return {"msg": "disconnected"}

def disconnect_ac():
    core_func.stop_connection_ac()
    return {"msg": "disconnected"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("connect ac and renderer")
    # Connect to the renderer microservice and animation controller on startup
    await establish_connection_ac()
    t1 = threading.Thread(target=establish_connection_renderer)
    t1.start()
    logger.info("ac and renderer connected")
    yield
    # Disconnect on shutdown
    logger.info("disconnect ac and renderer")
    disconnect_ac()
    disconnect_renderer()

app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_convesation = [{"role": "system", "content": "You are Elisa reception agent that can handle visitor checkin and answer all information related to Elisa Oyj. Elisa Oyj is a telecommunications, ICT and online service company operating in Finland. Keep your answers short and on point."},]
chatEngine = ChatEngine(init_convesation)
tts = AzureTextToSpeech()
checkin_handler = CheckinHandler()

SERVER_STATUS = "Ready"

core_func = CoreAPIA2XInteraction()

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

def setServerStatus(status):
    global SERVER_STATUS 
    SERVER_STATUS = status


@app.get("/")
def read_root():    
    return {"Hello": "World"}

@app.get("/checkin/host_data")
def get_host_data():
    host_data = checkin_handler.get_host_list()
    return host_data 

@app.post("/checkin/inform_host")
def inform_host(checkinInterface: CheckinInterface):
    checkin_handler.inform_host(checkinInterface.host_email, checkinInterface.visitor_name)
    return "email sent"


@app.post("/emotion_state")
def set_emotion_state():
    ## TODO: ver2
    return

@app.get("/emotion_state")
def get_emotion_state():
    ## TODO: ver2
    return    


@app.post("/send/user_message")
def send_user_message(userMsg: Msg):
    try:
        core_func.send_state_to_anim_controller("thinking")
        user_input = userMsg.content    
        message = {"role": "user", "content": user_input}
        setServerStatus("Generating text response")
        response_text = chatEngine.create(message)

        setServerStatus("Generating speech response")
        tts.speech(response_text)

        setServerStatus("Streaming audio to Audio2Face")
        audiopath = "/home/metard/project/meta-human/user_app_v0.1.21/response.wav"
        core_func.send_state_to_anim_controller("talking")
        result = core_func.send_audio_file(audiopath, EMOTION_LIST)
        core_func.send_state_to_anim_controller("listening")
        logger.info(result)
        setServerStatus("Ready")
        return {'user_input': user_input, 'response_text': response_text}   
    except:
        setServerStatus("Ready")
        return {'user_input': user_input, 'response_text': '500'}
    
@app.post("/send/ai_message")
def send_ai_message(aiMsg: Msg):
    try:
        tts.speech(aiMsg.content)
    
        setServerStatus("Streaming audio to Audio2Face")
        audiopath = "/home/metard/project/meta-human/user_app_v0.1.21/response.wav"
        core_func.send_state_to_anim_controller("talking")
        result = core_func.send_audio_file(audiopath, EMOTION_LIST)
        core_func.send_state_to_anim_controller("listening")
        logger.info(result)
        setServerStatus("Ready")
        return {'status': "Ready", 'response_text': aiMsg.content}   
    except:
        setServerStatus("Ready")
        return {'status': "Ready", 'response_text': '500'}
