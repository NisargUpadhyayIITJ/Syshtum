import io
import base64
import json
import os
import time
import asyncio
import requests
import pandas as pd
from PIL import Image, ImageDraw
from loguru import logger



def validate_and_extract_image_data(data):
    logger.debug("validate_and_extract_image_data() function called.")
    if not data or "messages" not in data:
        raise ValueError("Invalid request, no messages found")

    messages = data["messages"]
    if (
        not messages
        or not isinstance(messages, list)
        or not messages[-1].get("image_url")
    ):
        raise ValueError("No image provided or incorrect format")

    image_data = messages[-1]["image_url"]["url"]
    if not image_data.startswith("data:image"):
        raise ValueError("Invalid image format")

    return image_data.split("base64,")[-1], messages


def get_label_coordinates(label, label_coordinates):
    """
    Retrieves the coordinates for a given label.

    :param label: The label to find coordinates for (e.g., "~1").
    :param label_coordinates: Dictionary containing labels and their coordinates.
    :return: Coordinates of the label or None if the label is not found.
    """
    logger.debug("get_label_coordinates() function called.")
    return label_coordinates.get(label)


def is_overlapping(box1, box2):
    x1_box1, y1_box1, x2_box1, y2_box1 = box1
    x1_box2, y1_box2, x2_box2, y2_box2 = box2

    # Check if there is no overlap
    if x1_box1 > x2_box2 or x1_box2 > x2_box1:
        return False
    if (
        y1_box1 > y2_box2 or y1_box2 > y2_box1
    ):  # Adjusted to check 100px proximity above
        return False

    return True


def add_labels(base64_data, yolo_model):
    logger.debug("In the add labels function.")
    image_bytes = base64.b64decode(base64_data)
    image_labeled = Image.open(io.BytesIO(image_bytes))  # Corrected this line
    image_debug = image_labeled.copy()  # Create a copy for the debug image
    image_original = image_labeled.copy()  # Copy of the original image for base64 return
    logger.debug("Created image copies for debug and original versions")

    results = yolo_model(image_labeled)
    logger.debug("Yolo model instantiated.")

    draw = ImageDraw.Draw(image_labeled)
    debug_draw = ImageDraw.Draw(
        image_debug
    )  # Create a separate draw object for the debug image
    font_size = 45
    logger.debug(f"Initialized drawing contexts with font size: {font_size}")

    labeled_images_dir = "labeled_images"
    label_coordinates = {}  # Dictionary to store coordinates

    if not os.path.exists(labeled_images_dir):
        os.makedirs(labeled_images_dir)
        logger.debug(f"Created output directory: {labeled_images_dir}")

    counter = 0
    drawn_boxes = []  # List to keep track of boxes already drawn
    for result_idx, result in enumerate(results):
        logger.debug(f"Processing result {result_idx + 1}/{len(results)}")
        if hasattr(result, "boxes"):
            logger.debug(f"Found boxes in result {result_idx + 1}. Processing {len(result.boxes)} boxes")
            
            for det_idx, det in enumerate(result.boxes):
                bbox = det.xyxy[0]
                x1, y1, x2, y2 = bbox.tolist()
                logger.debug(f"Box {det_idx + 1} coordinates: x1={x1:.2f}, y1={y1:.2f}, x2={x2:.2f}, y2={y2:.2f}")

                debug_label = "D_" + str(counter)
                debug_index_position = (x1, y1 - font_size)
                debug_draw.rectangle([(x1, y1), (x2, y2)], outline="blue", width=1)
                debug_draw.text(
                    debug_index_position,
                    debug_label,
                    fill="blue",
                    font_size=font_size,
                )
                logger.debug(f"Drew debug box with label {debug_label}")

                overlap = any(
                    is_overlapping((x1, y1, x2, y2), box) for box in drawn_boxes
                )
                logger.debug(f"Box {det_idx + 1} overlap status: {overlap}")

                if not overlap:
                    draw.rectangle([(x1, y1), (x2, y2)], outline="red", width=1)
                    label = "~" + str(counter)
                    index_position = (x1, y1 - font_size)
                    draw.text(
                        index_position,
                        label,
                        fill="red",
                        font_size=font_size,
                    )

                    # Add the non-overlapping box to the drawn_boxes list
                    drawn_boxes.append((x1, y1, x2, y2))
                    label_coordinates[label] = (x1, y1, x2, y2)
                    logger.debug(f"Added non-overlapping box with label {label}")

                    counter += 1

    print(label_coordinates)

    # Save the image
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    logger.debug(f"Generated timestamp: {timestamp}")

    output_path = os.path.join(labeled_images_dir, f"img_{timestamp}_labeled.png")
    output_path_debug = os.path.join(labeled_images_dir, f"img_{timestamp}_debug.png")
    output_path_original = os.path.join(
        labeled_images_dir, f"img_{timestamp}_original.png"
    )

    image_labeled.save(output_path)
    image_debug.save(output_path_debug)
    image_original.save(output_path_original)
    logger.debug(f"Saved images to disk: {output_path}, {output_path_debug}, {output_path_original}")


    buffered_original = io.BytesIO()
    image_original.save(buffered_original, format="PNG")  # I guess this is needed
    img_base64_original = base64.b64encode(buffered_original.getvalue()).decode("utf-8")
    logger.debug("Converted original image to base64")

    # Convert image to base64 for return
    buffered_labeled = io.BytesIO()
    image_labeled.save(buffered_labeled, format="PNG")  # I guess this is needed
    img_base64_labeled = base64.b64encode(buffered_labeled.getvalue()).decode("utf-8")
    logger.debug("Converted labeled image to base64")

    logger.debug(f"Function complete. Processed {counter} non-overlapping boxes")
    return img_base64_labeled, label_coordinates


def get_click_position_in_percent(coordinates, image_size):
    """
    Calculates the click position at the center of the bounding box and converts it to percentages.

    :param coordinates: A tuple of the bounding box coordinates (x1, y1, x2, y2).
    :param image_size: A tuple of the image dimensions (width, height).
    :return: A tuple of the click position in percentages (x_percent, y_percent).
    """
    logger.debug("In the get_click_position_in_percent() function.")
    logger.debug(f"Coordinates: {coordinates}, Image_size: {image_size}")
    if not coordinates or not image_size:
        return None
    logger.debug("Passed the IF statement")

    # Calculate the center of the bounding box
    x_center = (coordinates[0] + coordinates[2]) / 2
    y_center = (coordinates[1] + coordinates[3]) / 2
    logger.debug(f"X-center: {x_center} and Y-center: {y_center}")

    # Convert to percentages
    # x_percent = x_center / image_size[0]
    # y_percent = y_center / image_size[1]
    x_percent = x_center
    y_percent = y_center 
    logger.debug(f"X-percent: {x_percent} and Y-percent: {y_percent}")

    return x_percent, y_percent


def add_custom_labels(base64_data):
    logger.debug("In the custom add labels function.")
    image_bytes = base64.b64decode(base64_data)
    logger.debug("Created image copies for debug and original versions")

    # results = yolo_model(image_labeled)
    response = requests.post(
            url='http://localhost:8001/label/',
            json={"image_base64": base64_data}    
        )

    logger.debug("Response received") 

    data = response.json()
    image_labeled = data["image"]
    parsed_content_list = data["coordinates"]

    logger.success("Parsed Content List")
    print(parsed_content_list)

    labeled_images_dir = "labeled_images"

    if not os.path.exists(labeled_images_dir):
        os.makedirs(labeled_images_dir)
        logger.debug(f"Created output directory: {labeled_images_dir}")

    # Save the image
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    logger.debug(f"Generated timestamp: {timestamp}")

    output_path = os.path.join(labeled_images_dir, f"img_{timestamp}_labeled.png")
    output_path_original = os.path.join(
        labeled_images_dir, f"img_{timestamp}_original.png"
    )


    # Open the labeled image (ensure it's a valid PIL Image)
    image_labeled = Image.open(io.BytesIO(base64.b64decode(image_labeled)))

    # Convert image to bytes (JPEG or PNG format)
    img_buffer = io.BytesIO()
    image_labeled.save(img_buffer, format="PNG")  # Change format if needed
    img_bytes = img_buffer.getvalue()

    # Encode image to base64 string
    base64_image = base64.b64encode(img_bytes).decode('utf-8')
    image_original = Image.open(io.BytesIO(image_bytes))

    image_labeled.save(output_path)
    image_original.save(output_path_original)
    logger.success("add_custom_labels() ended.")

    # buffered_original = io.BytesIO()
    # image_original.save(buffered_original, format="PNG")  # I guess this is needed
    # img_base64_original = base64.b64encode(buffered_original.getvalue()).decode("utf-8")
    # logger.debug("Converted original image to base64")

    # # Convert image to base64 for return
    # buffered_labeled = io.BytesIO()
    # image_labeled.save(buffered_labeled, format="PNG")  # I guess this is needed
    # img_base64_labeled = base64.b64encode(buffered_labeled.getvalue()).decode("utf-8")
    # logger.debug("Converted labeled image to base64")

    return base64_image, parsed_content_list
