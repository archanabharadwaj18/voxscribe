import numpy as np

def get_speakers(file_path):
    try:
        from simple_diarizer.diarizer import Diarizer
        
        diarizer = Diarizer(
            embed_model='xvec',
            cluster_method='ahc'
        )
        
        segments = diarizer.diarize(file_path, num_speakers=None)
        
        speakers = []
        for seg in segments:
            speakers.append({
                "start": seg['start'],
                "end": seg['end'],
                "speaker": f"Speaker {seg['label']}"
            })
        
        return speakers
        
    except Exception as e:
        print(f"[Diarizer] Error: {e}")
        return []


def assign_speakers_to_segments(transcript_segments, speaker_turns):
    if not speaker_turns:
        for segment in transcript_segments:
            segment["speaker"] = "Speaker 1"
        return transcript_segments

    for segment in transcript_segments:
        mid_time = (segment['start'] + segment['end']) / 2
        
        assigned_speaker = None

        for turn in speaker_turns:
            if turn['start'] <= mid_time <= turn['end']:
                assigned_speaker = turn['speaker']
                break

        if assigned_speaker is None:
            assigned_speaker = transcript_segments[0].get("speaker", "Speaker 1")

        segment['speaker'] = assigned_speaker
    
    return transcript_segments