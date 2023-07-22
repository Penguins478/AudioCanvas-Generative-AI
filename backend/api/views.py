from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AudioRecord
from .serializers import AudioRecordSerializer
import os
import openai
import warnings
from django.core.cache import cache
from rest_framework import status
import time
import math

warnings.filterwarnings("ignore")

openai.api_key = "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"

@api_view(['POST'])
def process_audio(request):
    if request.method == 'POST':
        # start = time.perf_counter()
        serializer = AudioRecordSerializer(data=request.data)

        # Get the 'use_cache' value from the request data
        use_cache = request.data.get('use_cache', False)
        # print(use_cache)

        if serializer.is_valid():
            serializer.save()
            audio_record = serializer.instance
            audio_path = audio_record.audio_file.path
            transcript, image_url = whisper_transcribe(audio_path, use_cache)
            audio_record.transcription = transcript
            audio_record.image_url = image_url
            audio_record.save()
            response_serializer = AudioRecordSerializer(audio_record)
            # end = time.perf_counter()
            # print("Time Elapsed (Backend): " + str(truncate(end - start, 2)) + "s")
            return Response(response_serializer.data)
        return Response(serializer.errors, status=400)
    return Response({'message': 'Invalid request'}, status=400)

def chatgpt_api(input_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    if input_text:
        messages.append(
            {"role": "user", "content": 'Summarize this text "{}" into a short and concise Dall-e2 prompt'.format(input_text)}
        )
        
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
    
    reply = chat_completion.choices[0].message.content
    return reply

def dall_e_api(dalle_prompt):
    dalle_response = openai.Image.create(
        prompt=dalle_prompt,
        size="512x512"
    )
    image_url = dalle_response['data'][0]['url']
    return image_url

def whisper_transcribe(audio, use_cache):
    os.rename(audio, audio + '.wav')
    audio_file = open(audio + '.wav', "rb")

    # Get the audio transcription
    transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]
    # print(use_cache)
    # print(type(use_cache))
    # Check if the image URL is already cached and the use_cache flag is True
    if use_cache == 'true':
        image_cache_key = f"image_url:{transcript}"
        image_url = cache.get(image_cache_key)   
        if image_url is not None:
            return transcript, image_url

    # if image_url is None:
    # Get the DALL-E prompt using the transcript
    dalle_prompt = chatgpt_api(transcript)

    # Generate the image URL using the DALL-E prompt
    image_url = dall_e_api(dalle_prompt)

    if use_cache == 'true':
        # Cache the image URL for future use
        cache.set(image_cache_key, image_url)

    return transcript, image_url

import math

def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

