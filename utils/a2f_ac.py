#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import asyncio
import uuid
import scipy
from nvidia_ace.animation_id.v1_pb2 import AnimationIds
from nvidia_ace.audio.v1_pb2 import AudioHeader
import numpy as np
from nvidia_ace.services.a2f.v1_pb2_grpc import A2FServiceStub
from nvidia_ace.a2f.v1_pb2 import AudioStream, AudioStreamHeader, AudioWithEmotion
import grpc
import requests


A2F_URL = "0.0.0.0:50000"
ANIMATIONMS_URL = "http://localhost:8020/"
RENDERERMS_URL = "http://localhost:8021/"
API_HEADERS = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}

# Sends an audio clip with the specified stream_id
# This stream_id allows to send multiple audio clips to the same avatar
async def write(stream, sample_rate: int, audio_data, stream_id):
    # Sends the audio stream header with audio metadata and ids
    # Refer to the proto files for more information
    await stream.write(
        AudioStream(
            audio_stream_header=AudioStreamHeader(
                audio_header=AudioHeader(
                    channel_count=1,
                    samples_per_second=sample_rate,
                    bits_per_sample=16,
                    audio_format=AudioHeader.AudioFormat.AUDIO_FORMAT_PCM,
                ),
                animation_ids=AnimationIds(
                    request_id=str(uuid.uuid4()),
                    target_object_id=str(uuid.uuid4()),
                    stream_id=stream_id,
                ),
            ),
        )
    )

    # Iterate over the audio data to send audio chunks
    for i in range(len(audio_data) // sample_rate + 1):
        # Create an audio chunk
        chunk = audio_data[i * sample_rate: i * sample_rate + sample_rate]
        # Send an audio chunk
        await stream.write(
            AudioStream(
                audio_with_emotion=AudioWithEmotion(
                    audio_buffer=chunk.astype(np.int16).tobytes(),
                    emotions=[],
                )
            )
        )
    # close the sending process
    await stream.done_writing()

class Controller():
    def __init__(self):
        self.a2f_url = A2F_URL
        self.animation_url = ANIMATIONMS_URL
        self.renderer_url = RENDERERMS_URL
        self.stream_id = ""

    def add_stream(self):
        if self.stream_id == "":
            self.stream_id = "101"
            data = {
                "event" : {
                    "camera_id" : self.stream_id
                }
            }

            renderer_respose = requests.post(self.renderer_url + "/sdr/add_stream", headers=API_HEADERS , json=data)
            animation_respose = requests.post(self.animation_url + "/sdr/add_stream", headers=API_HEADERS , json=data)
            return {"renderer": renderer_respose, "animation": animation_respose}
        else:
            return {"Stream id existed"}
        
    def remove_stream(self):
        if self.stream_id != "":
            data = {
                "event" : {
                    "camera_id" : self.stream_id
                }
            }

            renderer_respose = requests.post(self.renderer_url + "/sdr/remove_stream", headers=API_HEADERS , json=data)
            animation_respose = requests.post(self.animation_url + "/sdr/remove_stream", headers=API_HEADERS , json=data)
            if renderer_respose.status_code == 200 and animation_respose.status_code == 200:
                self.stream_id = ""
                return {"renderer": renderer_respose, "animation": animation_respose}
        else:
            return {"No stream id found"}
    
    def push_posture(self, posture):
        response = requests.put(self.animation_url + "/streams/{}/animation_graphs/avatar/variables/posture_state/{}".format(self.stream_id, posture), headers=API_HEADERS)
        return {"animation": response}
    
    def push_gesture(self, gesture):
        response = requests.put(self.animation_url + "/streams/{}/animation_graphs/avatar/variables/gesture_state/{}".format(self.stream_id, gesture), headers=API_HEADERS)
        return {"animation": response}


    async def push_audio(self, file):
        sample_rate, data = scipy.io.wavfile.read(file)

        # create a gRPC channel
        async with grpc.aio.insecure_channel(A2F_URL) as channel:
            # create gRPC stub and stream
            stub = A2FServiceStub(channel)
            stream = stub.PushAudioStream()
            # Send the audio clip
            await write(stream, sample_rate, data, self.stream_id)
            print(await stream)
        return


parser = argparse.ArgumentParser(
    description="Sample application to validate A2F setup.",
    epilog="NVIDIA CORPORATION.  All rights reserved.",
)

parser.add_argument("file", help="PCM-16 bits mono Audio file to send to the pipeline")
parser.add_argument("-u", "--url", help="URL of the Audio2Face Microservice", required=True)
parser.add_argument("-i", "--id", help="Stream ID for the request", required=True)



async def main():
    args = parser.parse_args()

    # extract sample rate and audio data from the provided audio file
    sample_rate, data = scipy.io.wavfile.read(args.file)

    # create a gRPC channel
    async with grpc.aio.insecure_channel(args.url) as channel:
        # create gRPC stub and stream
        stub = A2FServiceStub(channel)
        stream = stub.PushAudioStream()
        # Send the audio clip
        await write(stream, sample_rate, data, args.id)
        print(await stream)


if __name__ == "__main__":
    asyncio.run(main())
