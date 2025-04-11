from openai import OpenAI
from loguru import logger
import os

def text_to_speech(input, model="gpt-4o-mini-tts", voice="alloy"):
    client = OpenAI()
    with client.audio.speech.with_streaming_response.create(
        voice=voice,
        input=input,
        model=model,
        response_format="mp3",
    ) as response:
        response.stream_to_file(file='output.mp3')
        logger.success("Text to speech conversion successful.")
        os.system("afplay output.mp3") 
        logger.success("Playing audio file.")


if __name__ == "__main__":
    text_to_speech(input="Fuzzy matching After this first coarse document splitting we try to find the exact position within the paragraph.")

