import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("VoxScribe")

tab1, tab2 = st.tabs(["New Meeting", "Past Meetings"])

with tab1:
    meeting_name = st.text_input("Meeting name")
    uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3"])

    if uploaded_file and meeting_name:
        if st.button("Process Meeting"):
            with st.spinner("Processing, this may take a few minutes..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    data={"meeting_name": meeting_name},
                    files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                )

            if response.status_code == 200:
                result = response.json()
                st.success("Meeting processed and saved.")

                st.subheader("Language")
                st.write(f"{result['language']} ({result['language_confidence']}%)")

                st.subheader("Speaker-wise Transcript")
                for seg in result["segments"]:
                    speaker = seg.get("speaker", "Speaker 1")
                    text = seg.get("text", "")
                    st.markdown(f"**{speaker}:** {text}")
                
                st.subheader("Transcript")
                st.write(result["transcript"])

                st.subheader("Summary")
                st.write(result["summary"])

                st.subheader("Key Points")
                for point in result["key_points"]:
                    st.write("- " + point)

                st.subheader("Action Items")
                for item in result["action_items"]:
                    st.write("- " + item)
            else:
                st.error(f"Error: {response.text}")

with tab2:
    st.subheader("Past Meetings")
    
    if st.button("Refresh List"):
        st.rerun()

    response = requests.get(f"{API_URL}/meetings")
    if response.status_code == 200:
        meetings = response.json()
        if not meetings:
            st.write("No past meetings found.")
        else:
            for m in meetings:
                m_id = m['_id']
                
                with st.expander(f" {m['name']} ({m['date']})"):
                    new_name = st.text_input("Change Meeting Name", value=m['name'], key=f"edit_input_{m_id}")
                    if st.button("Update Name", key=f"update_btn_{m_id}"):
                        edit_resp = requests.put(f"{API_URL}/meetings/{m_id}?new_name={new_name}")
                        if edit_resp.status_code == 200:
                            st.success("Name updated!")
                            st.rerun()
                    
                    st.divider()

                    if st.button("View full details", key=f"view_{m_id}"):
                        full = requests.get(f"{API_URL}/meetings/{m_id}").json()
                        st.write("**Summary:**")
                        st.write(full["summary"])

                        st.write("**Language:**")
                        st.write(f"{full['language']} ({full['language_confidence']}%)")

                        st.write("**Speaker-wise Transcript:**")
                        for seg in full.get("segments", []):
                            speaker = seg.get("speaker", "Speaker 1")
                            text = seg.get("text", "")
                            st.markdown(f"**{speaker}:** {text}")

                        st.write("**Transcript:**")
                        st.write(full["transcript"])

          
                    with st.popover(" Delete Meeting"):
                        st.warning("Are you sure? This cannot be undone.")
                        if st.button("Confirm Delete", key=f"confirm_del_{m_id}"):
                            del_resp = requests.delete(f"{API_URL}/meetings/{m_id}")
                            if del_resp.status_code == 200:
                                st.toast(f"Deleted {m['name']}")
                                st.rerun()
    else:
        st.error("Could not load meetings.")