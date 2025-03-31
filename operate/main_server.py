from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from loguru import logger
from operate import main
from fastapi.middleware.cors import CORSMiddleware
from config import Config

# Create FastAPI app
app = FastAPI()

# adding cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"], 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Type", "Content-Length"],
    max_age=600,
)

class ValidateRequest(BaseModel):
    model: str

class PromptRequest(BaseModel):
    model: str
    prompt: str

class APIKeyRequest(BaseModel):
    model: str
    api_key: str


@app.post("/pipeline/")
def main_entry(request: PromptRequest) -> JSONResponse:
    logger.debug(f"Received request with model: {request.model} and prompt: {request.prompt}")
    try:
        config = Config()
        if(config.validation(request.model, voice_mode=False)):
            return JSONResponse(status_code=404, content={"status": "Error", "message": "Enter API Key"})
        main(
            model = request.model,
            terminal_prompt = request.prompt,
        )
        return JSONResponse(status_code=200, content={"status": "OK", "message": "Success"})
    except KeyboardInterrupt:
        print("\nExiting...")
        return JSONResponse(status_code=500, content={"status": "Error", "message": "Operation interrupted"})


@app.post("/validate/")
def validate(request: ValidateRequest) -> JSONResponse:
    config = Config()
    if(config.validation(request.model, voice_mode=False)):
        return JSONResponse(status_code=404, content={"status": "Error", "message": "Enter API Key"})
    # Add this return statement for the successful case
    return JSONResponse(status_code=200, content={"status": "OK", "message": "API Key valid"})

@app.post("/enter_api")
def enter_api(request: APIKeyRequest) -> JSONResponse:
    config = Config()
    config.save_api_key(request.model, request.api_key)
    return JSONResponse(status_code=200, content={"status": "OK", "message": "API Key saved"})


@app.post("/health")
def health_check():
    return JSONResponse(status_code=200, content={"status": "OK"})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)