from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel
import torch
from PIL import Image
import base64
import io
import os
import time
from util.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model

# Create FastAPI app
app = FastAPI()

# Global variables to store models
som_model = None
caption_model_processor = None
device = 'cpu'

class ImageRequest(BaseModel):
    image_base64: str

@app.on_event("startup")
async def load_models():
    """Initialize models when the FastAPI server starts"""
    global som_model, caption_model_processor
    
    logger.info("Loading models...")
    
    # Load SOM model
    model_path = 'weights/icon_detect/model.pt'
    som_model = get_yolo_model(model_path)
    som_model.to(device)
    logger.success("SOM model loaded and moved to GPU")
    
    # Load caption model
    caption_model_processor = get_caption_model_processor(
        model_name="florence2",
        model_name_or_path="weights/icon_caption_florence",
        device=device
    )
    logger.success("Caption model loaded")

async def process_image(encoded_image: str):
    """Process a single image using the pre-loaded models"""
    image = Image.open(io.BytesIO(base64.b64decode(encoded_image)))
    
    # Create temporary directory for image
    image_dir = "image_dir"
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, "screenshot.png")
    image.save(image_path)
    
    # Configure processing parameters
    box_overlay_ratio = max(image.size) / 3200
    draw_bbox_config = {
        'text_scale': 0.8 * box_overlay_ratio,
        'text_thickness': max(int(2 * box_overlay_ratio), 1),
        'text_padding': max(int(3 * box_overlay_ratio), 1),
        'thickness': max(int(3 * box_overlay_ratio), 1),
    }
    BOX_TRESHOLD = 0.05
    
    # Process OCR
    ocr_bbox_rslt, _ = check_ocr_box(
        image_path,
        display_img=False,
        output_bb_format='xyxy',
        goal_filtering=None,
        easyocr_args={'paragraph': False, 'text_threshold': 0.8},
        use_paddleocr=True
    )
    text, ocr_bbox = ocr_bbox_rslt
    
    # Process image with pre-loaded models
    dino_labled_img, _, parsed_content_list = get_som_labeled_img(
        image_path,
        som_model,
        BOX_TRESHOLD=BOX_TRESHOLD,
        output_coord_in_ratio=True,
        ocr_bbox=ocr_bbox,
        draw_bbox_config=draw_bbox_config,
        caption_model_processor=caption_model_processor,
        ocr_text=text,
        use_local_semantics=True,
        iou_threshold=0.7,
        scale_img=False,
        batch_size=128
    )
    
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)
    
    return dino_labled_img, parsed_content_list

@app.post("/label/")
async def generate(request: ImageRequest):
    """Handle incoming requests using pre-loaded models"""
    try:
        if som_model is None or caption_model_processor is None:
            raise HTTPException(
                status_code=503,
                detail="Models are not loaded yet. Please try again in a few moments."
            )
        
        logger.info("Processing request...")
        begin = time.time()
        dino_labled_img, parsed_content_list = await process_image(request.image_base64)
        logger.success("Request processed successfully")
        end = time.time()
        logger.success(f"Process completed sent in : {end - begin} seconds.")
        
        return JSONResponse({
            "image": dino_labled_img,
            "coordinates": parsed_content_list
        })
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)