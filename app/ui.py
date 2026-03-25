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
    
    if st.button("Refresh"):
        st.rerun()

    response = requests.get(f"{API_URL}/meetings")
    if response.status_code == 200:
        meetings = response.json()
        if not meetings:
            st.write("No past meetings found.")
        else:
            for m in meetings:
                with st.expander(f"{m['name']} - {m['date']}"):
                    st.write(m["summary"])
                    if st.button("View full details", key=f"view_{m['_id']}"):
                        full = requests.get(f"{API_URL}/meetings/{m['_id']}").json()
                        st.write("Transcript:")
                        st.write(full["transcript"])
                        st.write("Key Points:")
                        for kp in full["key_points"]:
                            st.write("- " + kp)
                        st.write("Action Items:")
                        for ai in full["action_items"]:
                            st.write("- " + ai)