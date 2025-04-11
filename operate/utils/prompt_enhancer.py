from openai import OpenAI
from google import genai
import os
from loguru import logger

def prompt_enhancement_gpt(prompt: str) -> str:
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f'''Analyse the given objective and elaborate it in order to make it clear to the LLMs on what actions need to be performed. Remember the output will be given to an OS LLM. Do not give any irrelevant information.
                \n\nObjective: {prompt}'''
            }
        ]
    )
    logger.success(f"Enhanced prompt: {completion.choices[0].message.content}")
    return completion.choices[0].message.content

def prompt_enhancement_gemini(prompt: str) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f'''Analyse the given objective and elaborate it in order to make it clear to the LLMs on what actions need to be performed. Remember the output will be given to an OS LLM. Do not give any irrelevant information.
            \n\nObjective: {prompt}'''
        ]
    )
    logger.success(f"Enhanced prompt: {response.text}")
    return response.text

if __name__ == "__main__":
    print(prompt_enhancement_gpt("Play Fuel by Eminem on Spotify."))

