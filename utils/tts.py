import os
import azure.cognitiveservices.speech as speechsdk


class AzureTextToSpeech():
    def __init__(self):
        self.speech_key = os.environ.get('AZURESPEECHKEY')
        self.service_region = "northeurope"

    def speech(self, text, language):
        speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, region=self.service_region)
        audio_config = speechsdk.audio.AudioOutputConfig(filename="./response.wav")
        if language == "en-US":
            input_ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US"><voice name="en-US-JennyNeural"><mstts:express-as style="customerservice" styledegree="2">{}</mstts:express-as></voice></speak>'.format(text)
        # use the default speaker as audio output.
        else:
            input_ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="fi-FI"><voice name="fi-FI-NooraNeural"><mstts:express-as style="customerservice" styledegree="2">{}</mstts:express-as></voice></speak>'.format(text)
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config)

        result = speech_synthesizer.speak_ssml_async(ssml=input_ssml).get()
        return result