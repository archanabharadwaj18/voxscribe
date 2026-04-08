# def combine_transcript_with_speakers(segments, speakers):
#     result = []

#     for seg in segments:
#         seg_mid = (seg["start"] + seg["end"]) / 2
#         matched_speaker = "Unknown"

#         for sp in speakers:
#             if sp["start"] <= seg_mid <= sp["end"]:
#                 matched_speaker = sp["speaker"]
#                 break

#         result.append(f"{matched_speaker}: {seg['text']}")

#     return "\n".join(result)  