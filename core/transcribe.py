from faster_whisper import WhisperModel

_model = None

def get_model():
    global _model
    if _model is None:
        _model = WhisperModel("base", compute_type="int8")
    return _model

def transcribe_audio(file_path):
    model = get_model()
    segments, info = model.transcribe(file_path, beam_size=5)

    result = []
    full_text = ""

    for segment in segments:
        result.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
        full_text += segment.text + " "

    detected_language = info.language
    confidence = round(info.language_probability * 100, 1)

    return full_text.strip(), result, detected_language, confidence