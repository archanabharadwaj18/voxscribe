# import os
# from pyannote.audio import Pipeline
# from dotenv import load_dotenv

# load_dotenv()

# _pipeline = None

# def get_pipeline():
#     global _pipeline
#     if _pipeline is None:
#         token = os.getenv("HF_TOKEN")
#         _pipeline = Pipeline.from_pretrained(
#             "pyannote/speaker-diarization-3.1",
#             token=token
#         )
#     return _pipeline

# def get_speakers(file_path):
#     pipeline = get_pipeline()
#     diarization = pipeline(file_path)

#     speakers = []
#     for turn, _, speaker in diarization.itertracks(yield_label=True):
#         speakers.append({
#             "start": turn.start,
#             "end": turn.end,
#             "speaker": speaker
#         })

#     return speakers