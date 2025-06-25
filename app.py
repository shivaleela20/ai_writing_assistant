import streamlit as st
import google.generativeai as genai
import os
import time


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    api_key = st.sidebar.text_input("Enter your Google Gemini API key:", type="password")
    if not api_key:
        st.stop()
    os.environ["GEMINI_API_KEY"] = api_key
    return api_key

def init_chat():
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model_name = st.sidebar.selectbox(
            "Select Gemini Model",
            ["gemini-1.5-flash", "gemini-1.5-pro"]
        )
        gen_model = genai.GenerativeModel(model_name)
        return gen_model, model_name
    except Exception as e:
        st.error(f"Error initializing Gemini API:"+str(e))
        return None, None

def main():
    st.set_page_config(page_title="Gemini AI writing Assistant",layout="wide")
    st.sidebar.header("Gemini AI Chat Assistant")
    api_key = init_session()

    st.title("Iterative AI Writing Assistant")
    st.markdown("""
    This tool allows you to interact with Google's Gemini AI for various writing tasks.
    Try asking the following  types of questions:
    -Writes a creativity story with characters and plot 
    -Generative a poem on a specific theme or about your pet/child/etc.
    -Create dialogue between characters for a scene 
    -Writes lyrics for a song with emotional context 
    Enter your prompt below and click "Generative Content" to start!
    """)
    col1,col2=st.columns(2)
    with col1:
       prompt_template = "Write an engineering story imagining:"
       user_prompt = st.text_area("Enter your creative prompt", placeholder=prompt_template, height=150).strip()

    if st.button("Generate Story"):
        with st.spinner("Gemini is crafting your story..."):
            try:
                prompt = "Write a creative, engaging, and narrative-rich story imagining:" +user_prompt

                # Prepare input with 'parts' key as expected by Gemini API
                gen_model,model_name=init_chat()
                if not gen_model:
                    st.error("Failed to initialize Gemini API")
                    return

                chat=gen_model.start_chat(history=st.session_state.messages)
                response=chat.send_message(prompt,stream=True)


                story = ""
                for chunk in response:
                    if hasattr(chunk, "text"):
                        story += chunk.text

                        time.sleep(0.03)

                # Save conversation history (store user prompt and assistant response)
                st.session_state.messages.append({"role": "user", "content": user_prompt})
                st.session_state.messages.append({"role": "assistant", "content": story})


            except Exception as e:
                st.error("Error generating content:"+ str(e))
                with col2:
                    if len(st.session_state.messages)>0:
                        st.header(" Conversation History")
                        display_messages = st.session_state.messages[-10:]
                        chat_container = st.container(height=400)
                        with chat_container:
                            for i,msg in enumerate(display_messages):
                                role="Human"if msg["role"]=="user"else "Gemini"
                                with st.chat_message(role):
                                    if msg["role"]=="user":
                                        st.markdown(f"**You:**{msg['content']}")
                                    else:
                                        st.markdown(f"**Assistant:**{msg['content']}")
if __name__ == "__main__":
    main()

