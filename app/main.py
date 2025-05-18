from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from stt import transcribe_speech_to_text
from llm import generate_response
from tts import transcribe_text_to_speech
from g2p_id import G2P
import os

app = FastAPI()

@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    
    # Tahap 1: Speech to text
    try:
        user_text = transcribe_speech_to_text(audio_bytes)
        print(user_text)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to transcribe speech", "detail": str(e)})

    # Tahap 2: Generate response from LLM
    try:
        response_text = generate_response(user_text)
        print(response_text)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to generate response", "detail": str(e)})

    # Tahap 3: G2P conversion
    try:
        g2p = G2P()
        fonem = g2p(response_text)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed in G2P conversion", "detail": str(e)})

    # Tahap 4: Text to speech synthesis
    try:
        tts_output_path = transcribe_text_to_speech(fonem)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to synthesize speech", "detail": str(e)})

    # Cek apakah file hasil TTS ada
    if not os.path.exists(tts_output_path):
        raise HTTPException(status_code=500, detail="Synthesized audio file not found.")

    # Jika semua berhasil, kirim file audio
    return FileResponse(tts_output_path, media_type="audio/wav")
