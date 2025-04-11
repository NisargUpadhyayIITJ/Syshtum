import base64
import io
import json
import os
import time
import traceback

import easyocr
import ollama
import huggingface_hub
import pkg_resources
from PIL import Image
from ultralytics import YOLO
from loguru import logger
import time 
import requests
import pandas as pd


from operate.config import Config
from operate.exceptions import ModelNotRecognizedException
from operate.models.prompts import (
    get_system_prompt,
    get_user_first_message_prompt,
    get_user_prompt,
    get_som_prompt
)
from operate.utils.label import (
    add_labels,
    add_custom_labels,
    get_click_position_in_percent,
    get_label_coordinates,
)
from operate.utils.ocr import get_text_coordinates, get_text_element
from operate.utils.screenshot import capture_screen_with_cursor
from operate.utils.style import ANSI_BRIGHT_MAGENTA, ANSI_GREEN, ANSI_RED, ANSI_RESET

# Load configuration
config = Config()


async def get_next_action(model, messages, objective, session_id):
    logger.debug("Get_next_action has started.")
    if config.verbose:
        print("[Self-Operating Computer][get_next_action]")
        print("[Self-Operating Computer][get_next_action] model", model)
    if model == "local_qwen":
        logger.debug("Model used is Qwen 2.5 VL")
        return call_show_ui(messages), None   
    if model == "gpt-4":
        logger.debug("Model used is GPT-4")
        return call_gpt_4o(messages), None
    if model == "gpt-4-with-som":
        logger.debug("Model used is GPT-4-with-som")
        operation = await call_gpt_4o_labeled(messages, objective, model)
        return operation, None
    if model == "gpt-4-with-ocr":
        logger.debug("Model used is GPT-4-with-ocr")
        operation = await call_gpt_4o_with_ocr(messages, objective, model)
        return operation, None
    if model == "custom-gpt":
        logger.debug("Model used is Custom GPT")
        operation = await call_custom_gpt(messages, objective, model)
        return operation, None
    if model == "custom-gemini":
        logger.debug("Model used is Custom Gemini")
        operation = await call_custom_gemini(messages, objective, model)
        return operation, None
    if model == "fast-gpt":
        logger.debug("Model used is Fast GPT")
        operation = await call_fast_gpt(messages, objective, model)
        return operation, None
    if model == "gemini-pro-vision":
        logger.debug("Model used is Gemini-Pro")
        return call_gemini_pro_vision(messages, objective), None
    if model == "fast-gemini":
        logger.debug("Model used is Gemini-2.0-Flash-Lite")
        return call_fast_gemini(messages, objective), None
    if model == "llava":
        logger.debug("Model used is Ollama-Llava")
        operation = call_ollama_llava(messages)
        return operation, None

    raise ModelNotRecognizedException(model)


def call_gpt_4o(messages):
    begin = time.time()
    if config.verbose:
        print("[call_gpt_4_v]")
    time.sleep(1)
    client = config.initialize_openai()
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        with open(screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        if len(messages) == 1:
            user_prompt = get_user_first_message_prompt()
        else:
            user_prompt = get_user_prompt()

        if config.verbose:
            print(
                "[call_gpt_4_v] user_prompt",
                user_prompt,
            )

        vision_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }
        # Images are also stored in the history, can be useful while making UI (show reasoning)
        messages.append(vision_message)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            presence_penalty=1,
            frequency_penalty=1,
        )

        content = response.choices[0].message.content
        logger.debug("Response recieved")

        content = clean_json(content)
        print(content)

        assistant_message = {"role": "assistant", "content": content}
        if config.verbose:
            print(
                "[call_gpt_4_v] content",
                content,
            )
        content = json.loads(content)

        # Output actions stored in history
        messages.append(assistant_message)
        end = time.time()
        logger.success(f"Call_gpt_4o executed in {end - begin}")
        return content, messages

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[Operate] That did not work. Trying again {ANSI_RESET}",
            e,
        )
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response was {ANSI_RESET}",
            content,
        )
        if config.verbose:
            traceback.print_exc()
        return call_gpt_4o(messages)


def call_gemini_pro_vision(messages, objective):
    """
    Get the next action for Self-Operating Computer using Gemini Pro Vision
    """
    begin = time.time()
    if config.verbose:
        print(
            "[Self Operating Computer][call_gemini_pro_vision]",
        )
    # sleep for a second
    time.sleep(1)
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)
        #image = Image.open(screenshot_filename)
        #messages.append(Image.open(screenshot_filename))
        # sleep for a second
        time.sleep(1)
        prompt = get_system_prompt("gemini-pro-vision", objective)
        logger.success("Got the system prompt.")

        model = config.initialize_google()
        logger.success("Gemini Client initialized")
        if config.verbose:
            print("[call_gemini_pro_vision] model", model)

        messages = [prompt, Image.open(screenshot_filename)]
        response = model.generate_content(messages)
        print(f"Response from gemini", response.text)
        logger.success("Response received")

        content = response.text#[1:]
        logger.success("Content created.")
        if config.verbose:
            print("[call_gemini_pro_vision] response", response)
            print("[call_gemini_pro_vision] content", content)

        logger.success("Starting Jsonification.")

        content = clean_json(content)
        print(content)
        logger.success("Cleaning done.")

        assistant_message = f'''"role": "assistant", "content": {content}'''
        prompt += assistant_message

        content = json.loads(content)
        logger.success("Jsonified.")

        if config.verbose:
            print(
                "[get_next_action][call_gemini_pro_vision] content",
                content,
            )    
        end = time.time()
        logger.success(f"Call_gemini_pro_vision executed in {end - begin}")
        return content, messages

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[Operate] That did not work. Trying another method {ANSI_RESET}"
        )
        if config.verbose:
            print("[Self-Operating Computer][Operate] error", e)
            traceback.print_exc()
        return call_gemini_pro_vision(messages, objective)


async def call_gpt_4o_with_ocr(messages, objective, model):
    begin = time.time()
    if config.verbose:
        print("[call_gpt_4o_with_ocr]")

    # Construct the path to the file within the package
    try:
        time.sleep(1)
        client = config.initialize_openai()
        logger.success("OpenAI Client Initialized")

        confirm_system_prompt(messages, objective, model)
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        with open(screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        if len(messages) == 1:
            user_prompt = get_user_first_message_prompt()
        else:
            user_prompt = get_user_prompt()

        vision_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }
        messages.append(vision_message)
        begin1 = time.time()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        content = response.choices[0].message.content
        end1 = time.time()
        logger.success(f"GPT-4o Inference time: {end1 - begin1}")

        content = clean_json(content)
        print(content)

        # used later for the messages
        content_str = content

        content = json.loads(content)

        processed_content = []

        for operation in content:
            logger.debug("Operation loop")
            if operation.get("operation") == "click":
                text_to_click = operation.get("text")
                if config.verbose:
                    print(
                        "[call_gpt_4o_with_ocr][click] text_to_click",
                        text_to_click,
                    )
                logger.success("Starting Easy OCR Reader")
                # Initialize EasyOCR Reader
                reader = easyocr.Reader(["en"])
                #ocr = PaddleOCR(use_angle_cls=True, lang='en')
                logger.success("Easy OCR Reader Initialized")

                # Read the screenshot
                result = reader.readtext(screenshot_filename)
                #result = ocr.ocr(screenshot_filename, cls=True)
                logger.success("Easy OCR Reader Output given below")
                print(result)

                text_element_index = get_text_element(
                    result, text_to_click, screenshot_filename
                )
                logger.debug(text_element_index)

                coordinates = get_text_coordinates(
                    result, text_element_index, screenshot_filename
                )
                logger.debug(coordinates)

                # add `coordinates`` to `content`
                operation["x"] = coordinates["x"]
                operation["y"] = coordinates["y"]

                if config.verbose:
                    print(
                        "[call_gpt_4o_with_ocr][click] text_element_index",
                        text_element_index,
                    )
                    print(
                        "[call_gpt_4o_with_ocr][click] coordinates",
                        coordinates,
                    )
                    print(
                        "[call_gpt_4o_with_ocr][click] final operation",
                        operation,
                    )
                processed_content.append(operation)
                logger.success("Content processed with OCR.")

            else:
                processed_content.append(operation)
                logger.success("Content processed without OCR.")

        # wait to append the assistant message so that if the `processed_content` step fails we don't append a message and mess up message history
        assistant_message = {"role": "assistant", "content": content_str}
        messages.append(assistant_message)

        end = time.time()
        logger.success(f"Call_gpt_4o_with_ocr executed in {end - begin}")
        return processed_content, messages

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[{model}] That did not work. Trying another method {ANSI_RESET}"
        )
        if config.verbose:
            print("[Self-Operating Computer][Operate] error", e)
            traceback.print_exc()
        return gpt_4_fallback(messages, objective, model)


async def call_gpt_4o_labeled(messages, objective, model):
    time.sleep(1)

    #try:
    client = config.initialize_openai()
    logger.debug("Client Initailized")

    confirm_system_prompt(messages, objective, model)
    #file_path = pkg_resources.resource_filename("models.weights", "best.pt")
    file_path = "./operate/models/weights/best.pt"
    #logger.debug("File path formed")

    yolo_model = YOLO(file_path)  # Load your trained model
    logger.debug("YOLO model loaded")

    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
    # Call the function to capture the screen with the cursor
    capture_screen_with_cursor(screenshot_filename)

    with open(screenshot_filename, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    img_base64_labeled, label_coordinates = add_labels(img_base64, yolo_model)

    if len(messages) == 1:
        user_prompt = get_user_first_message_prompt()
    else:
        user_prompt = get_user_prompt()

    if config.verbose:
        print(
            "[call_gpt_4_vision_preview_labeled] user_prompt",
            user_prompt,
        )

    vision_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": user_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64_labeled}"
                },
            },
        ],
    }
    messages.append(vision_message)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        presence_penalty=1,
        frequency_penalty=1,
    )

    content = response.choices[0].message.content

    content = clean_json(content)

    assistant_message = {"role": "assistant", "content": content}

    messages.append(assistant_message)

    content = json.loads(content)
    if config.verbose:
        print(
            "[call_gpt_4_vision_preview_labeled] content",
            content,
        )

    processed_content = []

    for operation in content:
        print(
            "[call_gpt_4_vision_preview_labeled] for operation in content",
            operation,
        )
        if operation.get("operation") == "click":
            logger.success("Click operation recieved.")
            label = operation.get("label")
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] label",
                    label,
                )

            coordinates = get_label_coordinates(label, label_coordinates)
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] coordinates",
                    coordinates,
                )
            image = Image.open(
                io.BytesIO(base64.b64decode(img_base64))
            )  # Load the image to get its size
            image_size = image.size  # Get the size of the image (width, height)
            click_position_percent = get_click_position_in_percent(
                coordinates, image_size
            )
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] click_position_percent",
                    click_position_percent,
                )
            if not click_position_percent:
                print(
                    f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Failed to get click position in percent. Trying another method {ANSI_RESET}"
                )
                return call_gpt_4o(messages)

            x_percent = f"{click_position_percent[0]:.2f}"
            y_percent = f"{click_position_percent[1]:.2f}"
            operation["x"] = x_percent
            operation["y"] = y_percent
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new click operation",
                    operation,
                )
            processed_content.append(operation)
        else:
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] .append none click operation",
                    operation,
                )

            processed_content.append(operation)

        if config.verbose:
            print(
                "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new processed_content",
                processed_content,
            )
    return processed_content, messages

    #except Exception as e:
    print(
        f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[{model}] That did not work. Trying another method {ANSI_RESET}"
    )
    if config.verbose:
        print("[Self-Operating Computer][Operate] error", e)
        traceback.print_exc()
    return call_gpt_4o(messages)


def call_ollama_llava(messages):
    begin = time.time()
    if config.verbose:
        print("[call_ollama_llava]")
    time.sleep(1)
    try:
        model = config.initialize_ollama()
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        with open(screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        if len(messages) == 1:
            user_prompt = get_user_first_message_prompt()
        else:
            user_prompt = get_user_prompt()

        if config.verbose:
            print(
                "[call_gpt_4_v] user_prompt",
                user_prompt,
            )

        vision_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }
        messages.append(vision_message)

        response = model.chat(
            model="llava",
            messages=messages,
        )

        # Important: Remove the image path from the message history.
        # Ollama will attempt to load each image reference and will
        # eventually timeout.
        messages[-1]["images"] = None

        content = response["message"]["content"].strip()

        content = clean_json(content)

        assistant_message = {"role": "assistant", "content": content}
        if config.verbose:
            print(
                "[call_ollama_llava] content",
                content,
            )
        content = json.loads(content)

        messages.append(assistant_message)
        end = time.time()
        logger.success(f"Call_ollama_llava executed in {end - begin}")
        return content, messages

    except ollama.ResponseError as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Operate] Couldn't connect to Ollama. With Ollama installed, run `ollama pull llava` then `ollama serve`{ANSI_RESET}",
            e,
        )

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[llava] That did not work. Trying again {ANSI_RESET}",
            e,
        )
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response was {ANSI_RESET}",
            content,
        )
        if config.verbose:
            traceback.print_exc()
        return call_ollama_llava(messages)
    
    
def call_show_ui(messages):
    """
    Get the next action for Self-Operating Computer using Gemini Pro Vision
    """
    begin = time.time()
    # sleep for a second
    time.sleep(1)

    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)
        #image = Image.open(screenshot_filename)
        #messages.append(Image.open(screenshot_filename))
        # sleep for a second

        with open(screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        if len(messages) == 1:
            user_prompt = get_user_first_message_prompt()
        else:
            user_prompt = get_user_prompt()

        vision_message ={
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    # {"type": "text", "text": PAST_ACTION},
                    {"type": "image", "image": f"data:image/jpeg;base64,{img_base64}"},
                ],
            }
        messages.append(vision_message)

        # Send the request
        response = requests.post(
            url='http://localhost:8001/generate/',
            json={
                "messages": messages
            }    
        )
        data = response.json()
        print(data)
        content = data["text"]
        print(content)
        logger.success("Response received")

        # Remove the last appended vision message to reduce input tokens
        messages.pop()

        # Convert response image back to PIL Image if needed
        # result_image = Image.open(BytesIO(base64.b64decode(data["image"])))
        # print("Text output:", content)
        # result_image.save("result.png")  # Save the result image if needed

        logger.success("Starting Jsonification.")

        content = clean_json(content)
        print(content)
        print(type(content))
        logger.success("Cleaning done.")

        assistant_message = {"role": "assistant", "content": content}
        messages.append(assistant_message)

        content = json.loads(content)
        print(content)    
        print(type(content))
        logger.success("Jsonified.")

        end = time.time()
        logger.success(f"Call_show_ui executed in {end - begin}")
        return content, messages

    except Exception as e:
        return call_show_ui(messages)

async def call_custom_gpt(messages, objective, model):
    time.sleep(1)

    #try:
    client = config.initialize_openai()
    logger.debug("Client Initailized")

    confirm_system_prompt(messages, objective, model)
    #file_path = pkg_resources.resource_filename("models.weights", "best.pt")

    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
    # Call the function to capture the screen with the cursor
    capture_screen_with_cursor(screenshot_filename)

    with open(screenshot_filename, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    if len(messages) == 1:
        user_prompt = get_user_first_message_prompt()
    else:
        user_prompt = get_user_prompt()

    if config.verbose:
        print(
            "[call_gpt_4_vision_preview_labeled] user_prompt",
            user_prompt,
        )

    vision_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": user_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"
                },
            },
        ],
    }
    messages.append(vision_message)

    begin_1 = time.time()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        presence_penalty=1,
        frequency_penalty=1,
    )
    end_1 = time.time()
    logger.success(f"GPT-4o responed on {end_1 - begin_1} seconds")

    content = response.choices[0].message.content

    content = clean_json(content)

    #Removes the vision message to reduce input tokens.
    messages.pop()

    assistant_message = {"role": "assistant", "content": content}

    messages.append(assistant_message)

    content = json.loads(content)
    if config.verbose:
        print(
            "[call_gpt_4_vision_preview_labeled] content",
            content,
        )

    processed_content = []

    for operation in content:
        print(
            "[call_gpt_4_vision_preview_labeled] for operation in content",
            operation,
        )
        if operation.get("operation") == "click":
            logger.success("Click operation received.")
            img_base64_labeled, parsed_content_list = add_custom_labels(img_base64)

            df = pd.DataFrame(parsed_content_list)
            df['ID'] = '~' + df.index.astype(str) # To match the previous version of code

            label_coordinates = dict(zip(df['ID'], df['bbox'])) # To match the previous version of code
            logger.success("Label Coordinates")
            print(label_coordinates)

            df = df.drop(columns=["bbox"]) # To reduce the input tokens to VLM

            label_message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": get_som_prompt(operation.get("thought"), df.to_markdown())},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64_labeled}"
                        },
                    },
                ],
            }

            begin_2 = time.time()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[label_message],
                presence_penalty=1,
                frequency_penalty=1,
            )
            end_2 = time.time()
            logger.success(f"GPT-4o responed for click on {end_2 - begin_2} seconds")

            response = response.choices[0].message.content
            logger.debug("Response")
            print(response)
            content = clean_json(response)

            dictionary = json.loads(content)

            logger.debug("Reason")
            print(dictionary["Reason"])

            label = dictionary["Label"]
            logger.success(f"VLM Output Label: {label}")
            label = "~" + str(label)
            #label = operation.get("label")

            coordinates = get_label_coordinates(label, label_coordinates)
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] coordinates",
                    coordinates,
                )
            image = Image.open(
                io.BytesIO(base64.b64decode(img_base64))
            )  # Load the image to get its size
            image_size = image.size  # Get the size of the image (width, height)
            click_position_percent = get_click_position_in_percent(
                coordinates, image_size
            )
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] click_position_percent",
                    click_position_percent,
                )
            if not click_position_percent:
                print(
                    f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Failed to get click position in percent. Trying another method {ANSI_RESET}"
                )
                return call_gpt_4o(messages)

            x_percent = f"{click_position_percent[0]:.2f}"
            y_percent = f"{click_position_percent[1]:.2f}"
            operation["x"] = x_percent
            operation["y"] = y_percent
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new click operation",
                    operation,
                )
            processed_content.append(operation)
        else:
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] .append none click operation",
                    operation,
                )

            processed_content.append(operation)

        if config.verbose:
            print(
                "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new processed_content",
                processed_content,
            )
    return processed_content, messages

async def call_custom_gemini(messages, objective, model):
    time.sleep(1)

    client = config.initialize_google()
    logger.debug("Client Initailized")

    confirm_system_prompt(messages, objective, model)

    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
    # Call the function to capture the screen with the cursor
    capture_screen_with_cursor(screenshot_filename)

    with open(screenshot_filename, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    if len(messages) == 1:
        user_prompt = get_user_first_message_prompt()
    else:
        user_prompt = get_user_prompt()

    if config.verbose:
        print(
            "[call_gemini_labeled] user_prompt",
            user_prompt,
        )

    vision_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": user_prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}"
                },
            },
        ],
    }
    messages.append(vision_message)

    begin_1 = time.time()
    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=messages,
        presence_penalty=1,
        frequency_penalty=1,
    )
    end_1 = time.time()
    logger.success(f"Gemini responed on {end_1 - begin_1} seconds")

    content = response.choices[0].message.content

    content = clean_json(content)

    #Removes the vision message to reduce input tokens.
    messages.pop()

    assistant_message = {"role": "assistant", "content": content}

    messages.append(assistant_message)

    content = json.loads(content)
    if config.verbose:
        print(
            "[call_gemini_labeled] content",
            content,
        )

    processed_content = []
    
    for operation in content:
        print(
            "[call_gemini_labeled] for operation in content",
            operation,
        )
        if operation.get("operation") == "click":
            logger.success("Click operation received.")
            img_base64_labeled, parsed_content_list = add_custom_labels(img_base64)

            df = pd.DataFrame(parsed_content_list)
            df['ID'] = '~' + df.index.astype(str)

            label_coordinates = dict(zip(df['ID'], df['bbox']))
            logger.success("Label Coordinates")
            print(label_coordinates)

            df = df.drop(columns=["bbox"])

            label_message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": get_som_prompt(operation.get("thought"), df.to_markdown())},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64_labeled}"
                        },
                    },
                ],
            }

            begin_2 = time.time()
            response = client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[label_message],
                presence_penalty=1,
                frequency_penalty=1,
            )
            end_2 = time.time()
            logger.success(f"Gemini responed for click on {end_2 - begin_2} seconds")

            response = response.choices[0].message.content
            logger.debug("Response")
            print(response)
            content = clean_json(response)

            dictionary = json.loads(content)

            logger.debug("Reason")
            print(dictionary["Reason"])

            label = dictionary["Label"]
            logger.success(f"VLM Output Label: {label}")
            label = "~" + str(label)

            coordinates = get_label_coordinates(label, label_coordinates)
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gemini_labeled] coordinates",
                    coordinates,
                )
            image = Image.open(
                io.BytesIO(base64.b64decode(img_base64))
            )
            image_size = image.size
            click_position_percent = get_click_position_in_percent(
                coordinates, image_size
            )
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gemini_labeled] click_position_percent",
                    click_position_percent,
                )
            if not click_position_percent:
                print(
                    f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Failed to get click position in percent. Trying another method {ANSI_RESET}"
                )
                return call_gemini_pro_vision(messages)
            
            x_percent = f"{click_position_percent[0]:.2f}"
            y_percent = f"{click_position_percent[1]:.2f}"
            operation["x"] = x_percent
            operation["y"] = y_percent
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gemini_labeled] new click operation",
                    operation,
                )
            processed_content.append(operation)
        else:
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gemini_labeled] .append none click operation",
                    operation,
                )
            processed_content.append(operation)

        if config.verbose:
            print(
                "[Self Operating Computer][call_gemini_labeled] new processed_content",
                processed_content,
            )
    return processed_content, messages

async def call_fast_gpt(messages, objective, model):
    time.sleep(1)

    #try:
    client = config.initialize_openai()
    logger.debug("Client Initailized")

    confirm_system_prompt(messages, objective, model)

    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
    # Call the function to capture the screen with the cursor
    capture_screen_with_cursor(screenshot_filename)

    with open(screenshot_filename, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    if len(messages) == 1:
        user_prompt = get_user_first_message_prompt()
    else:
        user_prompt = get_user_prompt()

    if config.verbose:
        print(
            "[call_gpt_4_vision_preview_labeled] user_prompt",
            user_prompt,
        )

    img_base64_labeled, parsed_content_list = add_custom_labels(img_base64)

    df = pd.DataFrame(parsed_content_list)
    df['ID'] = '~' + df.index.astype(str) # To match the previous version of code

    label_coordinates = dict(zip(df['ID'], df['bbox'])) # To match the previous version of code
    logger.success("Label Coordinates")
    print(label_coordinates)

    label_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": user_prompt},
            {"type": "text", "text": df.to_markdown()},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64_labeled}"
                },
            },
        ],
    }
    messages.append(label_message)

    begin = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        presence_penalty=1,
        frequency_penalty=1,
    )
    end = time.time()
    logger.success(f"GPT-4o responed on {end - begin} seconds")

    content = response.choices[0].message.content

    content = clean_json(content)

    messages.pop() #remove the unneccasry prompt

    assistant_message = {"role": "assistant", "content": content}

    messages.append(assistant_message)

    content = json.loads(content)
    if config.verbose:
        print(
            "[call_gpt_4_vision_preview_labeled] content",
            content,
        )

    processed_content = []

    for operation in content:
        print(
            "[call_gpt_4_vision_preview_labeled] for operation in content",
            operation,
        )
        if operation.get("operation") == "click":
            logger.success("Click operation recieved.")
            
            label = operation.get("label")
            logger.success(f"VLM Output Label: {label}")

            coordinates = get_label_coordinates(label, label_coordinates)
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] coordinates",
                    coordinates,
                )
            image = Image.open(
                io.BytesIO(base64.b64decode(img_base64))
            )  # Load the image to get its size
            image_size = image.size  # Get the size of the image (width, height)
            click_position_percent = get_click_position_in_percent(
                coordinates, image_size
            )
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] click_position_percent",
                    click_position_percent,
                )
            if not click_position_percent:
                print(
                    f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Failed to get click position in percent. Trying another method {ANSI_RESET}"
                )
                return call_gpt_4o(messages)

            x_percent = f"{click_position_percent[0]:.2f}"
            y_percent = f"{click_position_percent[1]:.2f}"
            operation["x"] = x_percent
            operation["y"] = y_percent
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new click operation",
                    operation,
                )
            processed_content.append(operation)
        else:
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] .append none click operation",
                    operation,
                )

            processed_content.append(operation)

        if config.verbose:
            print(
                "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new processed_content",
                processed_content,
            )
    return processed_content, messages

    #except Exception as e:
    print(
        f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[{model}] That did not work. Trying another method {ANSI_RESET}"
    )
    if config.verbose:
        print("[Self-Operating Computer][Operate] error", e)
        traceback.print_exc()
    return call_gpt_4o(messages) 

def call_fast_gemini(messages, objective):
    """
    Get the next action for Self-Operating Computer using Gemini Pro Vision
    """
    begin_1 = time.time()
    if config.verbose:
        print(
            "[Self Operating Computer][call_gemini_pro_vision]",
        )
    # sleep for a second
    time.sleep(1)
    # try:
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
    # Call the function to capture the screen with the cursor
    capture_screen_with_cursor(screenshot_filename)

    with open(screenshot_filename, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    #image = Image.open(screenshot_filename)
    #messages.append(Image.open(screenshot_filename))
    # sleep for a second
    time.sleep(1)
    logger.success("Got the system prompt.")

    if len(messages) == 1:
        user_prompt = get_user_first_message_prompt()
    else:
        user_prompt = get_user_prompt()

    model = config.initialize_google()
    logger.success("Gemini Client initialized")
    if config.verbose:
        print("[call_gemini_pro_vision] model", model)

    img_base64_labeled, parsed_content_list = add_custom_labels(img_base64)

    df = pd.DataFrame(parsed_content_list)
    df['ID'] = '~' + df.index.astype(str) # To match the previous version of code

    label_coordinates = dict(zip(df['ID'], df['bbox'])) # To match the previous version of code
    logger.success("Label Coordinates")
    print(label_coordinates)

    messages.append(user_prompt)
    messages.append(df.to_markdown())

    begin = time.time()
    response = model.generate_content(messages)
    end = time.time()

    print(f"Response from gemini", response.text)
    logger.success("Response received")

    content = response.text#[1:]
    logger.success("Content created.")
    if config.verbose:
        print("[call_gemini_pro_vision] response", response)
        print("[call_gemini_pro_vision] content", content)

    logger.success("Starting Jsonification.")

    content = clean_json(content)
    print(content)
    logger.success("Cleaning done.")

    messages.pop()
    assistant_message = f'''"role": "assistant", "content": {content}'''
    messages.append(assistant_message)

    content = json.loads(content)
    logger.success("Jsonified.")

    if config.verbose:
        print(
            "[get_next_action][call_gemini_pro_vision] content",
            content,
        )    

    processed_content = []

    for operation in content:
        print(
            "[call_gpt_4_vision_preview_labeled] for operation in content",
            operation,
        )
        if operation.get("operation") == "click":
            logger.success("Click operation recieved.")
            
            label = operation.get("label")
            logger.success(f"VLM Output Label: {label}")

            coordinates = get_label_coordinates(label, label_coordinates)
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] coordinates",
                    coordinates,
                )
            image = Image.open(
                io.BytesIO(base64.b64decode(img_base64))
            )  # Load the image to get its size
            image_size = image.size  # Get the size of the image (width, height)
            click_position_percent = get_click_position_in_percent(
                coordinates, image_size
            )
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] click_position_percent",
                    click_position_percent,
                )
            if not click_position_percent:
                print(
                    f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Failed to get click position in percent. Trying another method {ANSI_RESET}"
                )
                return call_gpt_4o(messages)

            x_percent = f"{click_position_percent[0]:.2f}"
            y_percent = f"{click_position_percent[1]:.2f}"
            operation["x"] = x_percent
            operation["y"] = y_percent
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new click operation",
                    operation,
                )
            processed_content.append(operation)
        else:
            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] .append none click operation",
                    operation,
                )

            processed_content.append(operation)

        if config.verbose:
            print(
                "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new processed_content",
                processed_content,
            )
    end_1 = time.time()
    logger.success(f"Call_gemini_pro_vision executed in {end_1 - begin_1}")
    return processed_content, messages

    # except Exception as e:
    #     print(
    #         f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[Operate] That did not work. Trying another method {ANSI_RESET}"
    #     )
    #     if config.verbose:
    #         print("[Self-Operating Computer][Operate] error", e)
    #         traceback.print_exc()
    #     return call_fast_gemini(messages, objective)

def get_last_assistant_message(messages):
    """
    Retrieve the last message from the assistant in the messages array.
    If the last assistant message is the first message in the array, return None.
    """
    logger.debug("get_last_assistant_message function executed.")
    for index in reversed(range(len(messages))):
        if messages[index]["role"] == "assistant":
            if index == 0:  # Check if the assistant message is the first in the array
                return None
            else:
                return messages[index]
    return None  # Return None if no assistant message is found


def gpt_4_fallback(messages, objective, model):
    begin = time.time()
    if config.verbose:
        print("[gpt_4_fallback]")
    system_prompt = get_system_prompt("gpt-4o", objective)
    new_system_message = {"role": "system", "content": system_prompt}
    # remove and replace the first message in `messages` with `new_system_message`

    messages[0] = new_system_message

    if config.verbose:
        print("[gpt_4_fallback][updated]")
        print("[gpt_4_fallback][updated] len(messages)", len(messages))
    end = time.time()
    logger.success(f"gpt_4_fallback function executed in {end - begin}")
    return call_gpt_4o(messages)


def confirm_system_prompt(messages, objective, model):
    """
    On `Exception` we default to `call_gpt_4_vision_preview` so we have this function to reassign system prompt in case of a previous failure
    """
    logger.debug("confirm_system_prompt function executed.")
    if config.verbose:
        print("[confirm_system_prompt] model", model)

    system_prompt = get_system_prompt(model, objective)
    new_system_message = {"role": "system", "content": system_prompt}
    # remove and replace the first message in `messages` with `new_system_message`

    messages[0] = new_system_message

    if config.verbose:
        print("[confirm_system_prompt]")
        print("[confirm_system_prompt] len(messages)", len(messages))
        for m in messages:
            if m["role"] != "user":
                print("--------------------[message]--------------------")
                print("[confirm_system_prompt][message] role", m["role"])
                print("[confirm_system_prompt][message] content", m["content"])
                print("------------------[end message]------------------")


def clean_json(content):
    logger.debug("clean_json function executed.")
    if config.verbose:
        print("\n\n[clean_json] content before cleaning", content)
    if content.startswith("```json"):
        content = content[
            len("```json") :
        ].strip()  # Remove starting ```json and trim whitespace
    elif content.startswith("```"):
        content = content[
            len("```") :
        ].strip()  # Remove starting ``` and trim whitespace
    if content.endswith("```"):
        content = content[
            : -len("```")
        ].strip()  # Remove ending ``` and trim whitespace

    # Normalize line breaks and remove any unwanted characters
    content = "\n".join(line.strip() for line in content.splitlines())

    if config.verbose:
        print("\n\n[clean_json] content after cleaning", content)

    return content
