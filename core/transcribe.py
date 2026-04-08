from faster_whisper import WhisperModel
from core.diarize import get_speakers, assign_speakers_to_segments

_model = None

INDIAN_LANGS = {
    "hi", "bn", "ta", "te", "mr", "gu",
    "kn", "ml", "pa", "ur"
}

def get_model():
    global _model
    if _model is None:
        _model = WhisperModel("small", compute_type="int8")
    return _model

def transcribe_audio(file_path):
    model = get_model()

    segments, info = model.transcribe(
        file_path,
        language="hi",
        beam_size=5,
        vad_filter=True,
        initial_prompt="यह एक हिंदी बातचीत है।"
    )

    result = []
    full_text = ""

    speaker_turns = get_speakers(file_path)

    for segment in segments:
        text = segment.text.strip()
        if text:
            result.append({
                "start": segment.start,
                "end": segment.end,
                "text": text
            })

    result = assign_speakers_to_segments(result, speaker_turns)

    for seg in result:
        speaker = seg.get("speaker", "Speaker 1")
        line = f"[{speaker}]: {seg['text']}"
        full_text += line + "\n"

    detected_language = info.language
    confidence = round(info.language_probability * 100, 1)

    detected_language = normalize_indian_language(
        detected_language,
        confidence
    )

    return full_text.strip(), result, detected_language, confidence


def normalize_indian_language(lang_code: str, confidence: float) -> str:
    if lang_code == "ur" and confidence < 85:
        return "hi"

    if lang_code == "kn" and confidence < 80:
        return "tulu"

    if lang_code == "ml" and confidence < 75:
        return "ta"

    if lang_code == "kn" and confidence > 80:
        return "te" if confidence < 90 else "kn"

    if lang_code == "bn" and confidence < 70:
        return "hi"

    if lang_code == "pa" and confidence < 75:
        return "hi"

    return lang_code