from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os  # <--- 1. NEW IMPORT (Safety for Vercel)

tags_metadata = [
    {
        "name": "Conversion",
        "description": "Operations to convert between Text and Morse code.",
    },
    {
        "name": "System",
        "description": "Health checks and status.",
    },
]

app = FastAPI(
    title="Morse Code Converter",
    description="A professional API that converts plain text into Morse code and vice versa.",
    version="1.0.0",
    contact={
        "name": "Anvin",
        "email": "student@tkmce.ac.in",
    },
    openapi_tags=tags_metadata
)

# --- MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DICTIONARY ---
MORSE_CODE_DICT =  {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
                   'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
                   'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
                   'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
                   'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
                   'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
                   '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
                   '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
                   '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...',
                   ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-',
                   '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'
                   }

REVERSE_DICT = {value: key for key, value in MORSE_CODE_DICT.items()}

# --- MODELS ---
class TextRequest(BaseModel):
    text: str = Field(..., example="HELLO WORLD")

class MorseRequest(BaseModel):
    morse_code: str = Field(..., example=".... . .-.. .-.. --- / .-- --- .-. .-.. -..")

# --- ENDPOINTS ---

@app.get("/", tags=["System"])
def home():
    """
    **Home Page**
    Serves the Morse Code Translator Interface.
    """
    # 2. SAFETY FIX: Get the absolute path to index.html
    # This prevents "File Not Found" errors on Vercel
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    return FileResponse(file_path)

@app.post("/text-to-morse", tags=["Conversion"])
def convert_text_to_morse(request: TextRequest):
    input_text = request.text.upper()
    if not input_text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    morse_output = []
    for char in input_text:
        if char in MORSE_CODE_DICT:
            morse_output.append(MORSE_CODE_DICT[char])
        elif char == ' ':
            morse_output.append('/') 
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported character: {char}")

    return {"original": input_text, "morse": " ".join(morse_output)}

@app.post("/morse-to-text", tags=["Conversion"])
def convert_morse_to_text(request: MorseRequest):
    input_morse = request.morse_code.strip()
    if not input_morse:
        raise HTTPException(status_code=400, detail="Input Morse code cannot be empty.")

    normalized_morse = input_morse.replace(' / ', '/')
    words = normalized_morse.split('/')
    decoded_message = []

    for word in words:
        if word == "": continue
        letters = word.strip().split(' ')
        decoded_word = ""
        for letter in letters:
            if letter in REVERSE_DICT:
                decoded_word += REVERSE_DICT[letter]
            else:
                raise HTTPException(status_code=400, detail=f"Invalid Morse sequence: {letter}")
        decoded_message.append(decoded_word)

    return {"original": input_morse, "text": " ".join(decoded_message)}
