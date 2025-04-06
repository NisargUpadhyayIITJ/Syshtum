from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import subprocess
import time
from pathlib import Path
from typing import List, Optional

app = FastAPI()

# Data directory
DATA_DIR = Path.home() / ".self_operating_computer"
DATA_DIR.mkdir(exist_ok=True)

# API keys file
API_KEYS_FILE = DATA_DIR / "api_keys.json"
if not API_KEYS_FILE.exists():
    with open(API_KEYS_FILE, 'w') as f:
        json.dump({"fast-gpt": "", "fast-gemini": ""}, f)

# Recent commands file
COMMANDS_FILE = DATA_DIR / "recent_commands.json"
if not COMMANDS_FILE.exists():
    with open(COMMANDS_FILE, 'w') as f:
        json.dump({"commands": []}, f)

# Models for request/response
class ApiKeyModel(BaseModel):
    model: str
    api_key: str

class ValidateModel(BaseModel):
    model: str

class CommandModel(BaseModel):
    model: str
    prompt: str

class SaveCommandModel(BaseModel):
    command: str

class CommandsResponse(BaseModel):
    commands: List[str]

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/enter_api")
def enter_api(data: ApiKeyModel):
    """Save API key for a model"""
    try:
        # Load existing keys
        with open(API_KEYS_FILE, 'r') as f:
            keys = json.load(f)
        
        # Update key for the model
        keys[data.model] = data.api_key
        
        # Save back to file
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(keys, f)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save API key: {str(e)}")

@app.post("/validate/")
def validate_api(data: ValidateModel):
    """Validate if API key exists for model"""
    try:
        # Load keys
        with open(API_KEYS_FILE, 'r') as f:
            keys = json.load(f)
        
        # Check if key exists and is not empty
        if data.model in keys and keys[data.model].strip():
            return {"status": "valid"}
        else:
            raise HTTPException(status_code=404, detail=f"API key not found for {data.model}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.post("/pipeline/")
def run_pipeline(data: CommandModel):
    """Execute a command using the specified model"""
    try:
        # Load API key for the model
        with open(API_KEYS_FILE, 'r') as f:
            keys = json.load(f)
        
        if data.model not in keys or not keys[data.model].strip():
            raise HTTPException(status_code=404, detail=f"API key not found for {data.model}")
        
        api_key = keys[data.model]
        
        # Set environment variable for the appropriate API key
        os.environ["API_KEY"] = api_key
        
        # Determine which script to run based on the model
        script_path = "operate/run.py"
        
        # Select model name for the script
        model_name = "gpt-4o" if data.model == "fast-gpt" else "gemini"
        
        # Run the command
        cmd = ["python", script_path, "--prompt", data.prompt, "--model", model_name]
        
        # Execute the process and capture output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the process to complete with a timeout
        try:
            stdout, stderr = process.communicate(timeout=60)  # 60 seconds timeout
            
            if process.returncode != 0:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Command execution failed: {stderr}"
                )
            
            # Add to recent commands
            save_command(SaveCommandModel(command=data.prompt))
            
            return {"status": "success", "output": stdout}
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise HTTPException(
                status_code=504,
                detail="Command execution timed out"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute command: {str(e)}"
        )

@app.post("/save_command/")
def save_command(data: SaveCommandModel):
    """Save a command to recent commands list"""
    try:
        # Load existing commands
        with open(COMMANDS_FILE, 'r') as f:
            commands_data = json.load(f)
        
        commands = commands_data.get("commands", [])
        
        # Remove duplicates
        if data.command in commands:
            commands.remove(data.command)
        
        # Add to the front
        commands.insert(0, data.command)
        
        # Trim to last 20 commands
        commands = commands[:20]
        
        # Save back to file
        with open(COMMANDS_FILE, 'w') as f:
            json.dump({"commands": commands}, f)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save command: {str(e)}"
        )

@app.get("/recent_commands/", response_model=CommandsResponse)
def get_recent_commands():
    """Get list of recent commands"""
    try:
        # Load commands
        with open(COMMANDS_FILE, 'r') as f:
            commands_data = json.load(f)
        
        return {"commands": commands_data.get("commands", [])}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent commands: {str(e)}"
        )

@app.delete("/clear_commands/")
def clear_commands():
    """Clear all recent commands"""
    try:
        # Save empty commands list
        with open(COMMANDS_FILE, 'w') as f:
            json.dump({"commands": []}, f)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear commands: {str(e)}"
        )