from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ### NEW IMPORT
from pydantic import BaseModel, Field

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
    description="A professional API that converts plain text into Morse code and vice versa. Developed for the recruitment task.",
    version="1.0.0",
    contact={
        "name": "Anvin (Your Name)",
        "email": "student@tkmce.ac.in",
    },
    openapi_tags=tags_metadata
)

# ### NEW: ADD THIS BLOCK AFTER app = FastAPI(...) ###
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your local HTML file to talk to the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ### END NEW BLOCK ###


# --- 2. THE DICTIONARY ---
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

# --- 3. DATA MODELS WITH EXAMPLES ---
class TextRequest(BaseModel):
    # This 'example' will appear automatically in the UI
    text: str = Field(..., example="HELLO WORLD", description="The plain text message to convert.")

class MorseRequest(BaseModel):
    # This 'example' will appear automatically in the UI
    morse_code: str = Field(..., example=".... . .-.. .-.. --- / .-- --- .-. .-.. -..", description="Morse code string. Use space for letters and / for words.")

# --- 4. TUNED ENDPOINTS ---

@app.get("/", tags=["System"])
def home():
    """
    **System Check**
    
    Returns a simple message to confirm the API is online.
    """
    return {"status": "online", "message": "Go to /docs to use the converter."}

@app.post("/text-to-morse", tags=["Conversion"], summary="Convert Text -> Morse")
def convert_text_to_morse(request: TextRequest):
    """
    **Converts Plain Text to Morse Code**
    
    - **Input:** Standard English text (A-Z, 0-9).
    - **Output:** Morse code string.
    - **Logic:** Letters separated by spaces, words separated by `/`.
    """
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

@app.post("/morse-to-text", tags=["Conversion"], summary="Convert Morse -> Text")
def convert_morse_to_text(request: MorseRequest):
    """
    **Converts Morse Code to Plain Text**
    
    - **Input:** String of dots and dashes.
    - **Output:** Decoded English text.
    - **Format:** Use `space` between letters and `/` between words.
    """
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
