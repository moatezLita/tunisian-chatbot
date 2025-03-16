import os
import logging
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Import your modules
from transliteration import TunisianTransliterator
from cultural_context import TunisianCulturalContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tunisian_chat.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Define request models
class ChatRequest(BaseModel):
    message: str
    scriptPreference: Optional[str] = "both"

class TransliterationRequest(BaseModel):
    text: str
    direction: Optional[str] = "auto"

# Initialize FastAPI app
app = FastAPI(title="Tunisian Dialect Chat")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Initialize components
transliterator = TunisianTransliterator()
cultural_context = TunisianCulturalContext()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat API endpoint"""
    try:
        # Process the message
        response = process_message(request.message, request.scriptPreference)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transliterate")
async def transliterate(request: TransliterationRequest):
    """Transliteration API endpoint"""
    try:
        if request.direction == "latin_to_arabic":
            result = transliterator.latin_to_arabic(request.text)
        elif request.direction == "arabic_to_latin":
            result = transliterator.arabic_to_latin(request.text)
        else:
            # Auto-detect and transliterate
            result = transliterator.auto_transliterate(request.text)
        
        return {"result": result}
    except Exception as e:
        logger.error(f"Error processing transliteration request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def process_message(message, script_preference="both"):
    """
    Process user message
    
    Args:
        message: User message
        script_preference: User's script preference
        
    Returns:
        Response message
    """
    # Detect script and analyze
    script_analysis = transliterator.detect_dialect_script_mix(message)
    
    # Extract cultural entities
    entities = cultural_context.extract_cultural_entities(message)
    
    # Generate a response based on the message content
    # This is where you would integrate with a language model or rule-based system
    
    # For now, create a simple response with cultural context
    if "ahla" in message.lower() or "أهلا" in message:
        response = "Ahla bik! Chneya n7eb n3awnek?"
        transliteration = "أهلا بيك! شنية نحب نعاونك؟"
    elif "labess" in message.lower() or "لاباس" in message:
        response = "Hamdullah, enti labess?"
        transliteration = "الحمد لله، انتي لاباس؟"
    elif "couscous" in message.lower() or "كسكسي" in message:
        response = "Ah, el couscous aklet Tounsiya tounsia barcha!"
        transliteration = "آه، الكسكسي أكلة تونسية برشا!"
    else:
        response = "Fhemtek. Zid a7kili 3la 7aja okhra."
        transliteration = "فهمتك. زيد احكيلي على حاجة أخرى."
    
    # Add transliteration based on script preference
    if script_preference == "arabic" or (script_analysis["primary_script"] == "Latin" and script_preference == "both"):
        response += f"<span class='transliteration'>{transliteration}</span>"
    elif script_preference == "latin" or (script_analysis["primary_script"] == "Arabic" and script_preference == "both"):
        response += f"<span class='transliteration'>{transliterator.arabic_to_latin(response)}</span>"
    
    # Add cultural context if entities were found
    if entities:
        response += "\n\n<strong>Cultural context:</strong>"
        for category, items in entities.items():
            for item in items:
                context = cultural_context.get_cultural_context(item, category)
                if context:
                    response += f"\n- <em>{item}</em>: {context.get('meaning', '')} ({context.get('context', '')})"
    
    return response

if __name__ == "__main__":
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Run the app
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)