"""
Self-Operating Computer
"""
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from loguru import logger
from operate import main
from fastapi.middleware.cors import CORSMiddleware



# Create FastAPI app
app = FastAPI()

# adding cors middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Type", "Content-Length"],
    max_age=600,
)


class PromptRequest(BaseModel):
    model: str
    prompt: str

@app.post("/pipeline/")
def main_entry(request: PromptRequest) -> None:
    logger.debug(f"Received request with model: {request.model} and prompt: {request.prompt}")
    try:
        main(
            model = request.model,
            terminal_prompt = request.prompt,
            #voice_mode=voice_mode,
        )
    except KeyboardInterrupt:
        print("\nExiting...")

@app.post("/health")
def health_check():
    return JSONResponse(status_code=200, content={"status": "OK"})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)