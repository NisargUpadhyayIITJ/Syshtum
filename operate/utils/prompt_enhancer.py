from openai import OpenAI
import google.generativeai as genai  
import os
from loguru import logger

def prompt_enhancement_gpt(prompt: str) -> str:
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f'''
                Analyze the following user objective and break it down into explicit, step-by-step actions for an OS-controlled LLM. 

                **Rules:**
                1. **Be specific**: Replace vague terms (e.g., "open") with exact actions
                2. **Prioritize keyboard shortcuts** over mouse clicks when possible.  
                3. **Assume default apps**: Use Chrome for browsing, Terminal for commands, unless specified.  

                **Objective:**  
                "{prompt}" '''
            }
        ]
    )
    logger.success(f"Enhanced prompt: {completion.choices[0].message.content}")
    return completion.choices[0].message.content

def prompt_enhancement_gemini(prompt: str) -> str:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY_1"))  
    model = genai.GenerativeModel("gemini-2.0-flash",)

    response = model.generate_content(
        contents=[
            f'''Analyze the following user objective and break it down into explicit, step-by-step actions for an OS-controlled LLM. 

            **Rules:**
            1. **Be specific**: Replace vague terms (e.g., "open") with exact actions
            2. **Prioritize keyboard shortcuts** over mouse clicks when possible.  
            3. **Assume default apps**: Use Chrome for browsing, Terminal for commands, unless specified.  

            **Objective:**  
            "{prompt}" '''
        ]
    )
    logger.success(f"Enhanced prompt: {response.text}")
    return response.text

if __name__ == "__main__":
    print(prompt_enhancement_gpt("Play Fuel by Eminem on Spotify."))

