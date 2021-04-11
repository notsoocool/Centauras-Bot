# coding=utf-8
# This is a sample Python script.
import webbrowser
from datetime import datetime

import PyPDF2 as PyPDF2
import grpc
import pyaudio
import wave
import asyncio
import uuid
import subprocess
import os
import re

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from speechly.identity.v2.identity_api_pb2 import LoginRequest
from speechly.identity.v2.identity_api_pb2_grpc import IdentityAPIStub
from speechly.identity.v2.identity_pb2 import ApplicationScope
from speechly.slu.v1.slu_pb2 import SLURequest, SLUEvent, SLUConfig
from speechly.slu.v1.slu_pb2_grpc import SLUStub

frames = []  # Initialize array to store frames


def fnPDF_FindText(xFile, xString):
    # xfile : the PDF file in which to look
    # xString : the string to look for
    PageFound = -1
    object = PyPDF2.PdfFileReader(xFile)

    # Get number of pages
    NumPages = object.getNumPages()

    # Extract text and do the search
    for i in range(0, NumPages):
        PageObj = object.getPage(i)
        Text = PageObj.extractText()
        if re.search(xString, Text):
            PageFound = i
            break
    return PageFound

def audio_stream():
    chunk = 8000  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 16000  # Record at 16000 samples per second
    seconds = 5
    filename = "output.wav"

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    return stream


async def login(channel, device_id, app_id=None, project_id=None):
    assert device_id, 'UUID device_is required'
    assert (app_id or project_id), 'app_id or project_id is required'
    identity_api = IdentityAPIStub(channel)
    req = LoginRequest(device_id=device_id, application=app_id)
    response = await identity_api.Login(req)
    token = response.token
    expires = datetime.fromisoformat(response.expires_at)
    return token, expires


async def stream_speech(channel, token, audio_stream, app_id=None):
    auth = ('authorization', f'Bearer {token}')

    async def read_responses(stream):
        transcript = []
        intent = ''
        entities = []
        resp = await stream.read()
        while resp != grpc.aio.EOF:
            if resp.HasField('started'):
                print(f'audioContext {resp.audio_context} started')
            elif resp.HasField('transcript'):
                transcript.append(resp.transcript.word)
            elif resp.HasField('entity'):
                entities.append(resp.entity.value)
            elif resp.HasField('intent'):
                intent = resp.intent.intent
            elif resp.HasField('finished'):
                print(f'audioContext {resp.audio_context} finished')
            resp = await stream.read()
        return intent, entities, transcript

    async def send_audio(stream, source):
        await stream.write(SLURequest(event=SLUEvent(event='START', app_id=app_id)))
        for chunk in frames:
            await stream.write(SLURequest(audio=chunk))
        await stream.write(SLURequest(event=SLUEvent(event='STOP')))
        await stream.done_writing()

    async with channel:
        slu = SLUStub(channel)
        try:
            stream = slu.Stream(metadata=[auth])
            config = SLUConfig(channels=1, sample_rate_hertz=16000)
            await stream.write(SLURequest(config=config))
            recv = read_responses(stream)
            send = send_audio(stream, audio_stream)
            r = await asyncio.gather(recv, send)
            intent, entities, transcript = r[0]
            print('Intent:', intent)
            print('Entities:', ', '.join(entities))
            print('Transcript:', ' '.join(transcript))

            if intent == 'open':
                page = 'page='+str(fnPDF_FindText('D:\Akshay\study_material\\Notes.pdf', str(entities[0])+' minutes'))
                print(page)
                path_to_pdf = os.path.abspath('D:\Akshay\study_material\\Notes.pdf')
                # I am testing this on my Windows Install machine
                path_to_acrobat = os.path.abspath('C:\Program Files (x86)\Adobe\Reader 10.0\Reader\AcroRd32.exe')

                # this will open your document on page 12
                process = subprocess.Popen([path_to_acrobat, '/A', page, path_to_pdf], shell=False,
                                           stdout=subprocess.PIPE)
                process.wait()

        except grpc.aio.AioRpcError as e:
            print('Error in SLU', str(e.code()), e.details())


async def main():
    stream = audio_stream()
    channel = grpc.aio.secure_channel(
        target='api.speechly.com:443',
        credentials=grpc.ssl_channel_credentials(),
        options=[('grpc.default_authority', 'api.speechly.com')]
    )

    x = uuid.UUID('{00010203-0405-0607-0809-0a0b0c0d0e0f}')
    device_id = uuid.uuid1()
    application = ApplicationScope(app_id="666fb1f1-45a7-4753-b3d0-e1fc7eed0849")
    app_id = "666fb1f1-45a7-4753-b3d0-e1fc7eed0849"

    token, expire = await login(channel, str(x), application, None)

    await stream_speech(channel, token, stream, app_id)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(main())
