from groq import Groq

TRANSCRIPTION_MODEL = "whisper-large-v3"
def transcribe_audio(client: Groq, file_bytes: bytes, filename: str)-> str:
    transcription = client.audio.transcriptions.create(
        file=(filename, file_bytes),
        model=TRANSCRIPTION_MODEL,
        response_format="text",
    )
    return transcription.strip() if isinstance(transcription, str) else transcription.text.strip()