import gradio as gr
import requests
from gradio_styles import Seafoam


API_URL = "http://localhost:8000/query"
seafoam=Seafoam()

def send_query(user_query):
    try:
        response = requests.post(API_URL, json={"query": user_query})
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response")
    except Exception as e:
        return f"Error: {e}"

with gr.Blocks(theme=seafoam) as iface:
    gr.Markdown("# Spam & biography talks")
    chatbot = gr.Chatbot(label="S&BT")
    with gr.Column():
        input_box = gr.Textbox(label="Question", placeholder="Enter your request:)")
        submit_btn = gr.Button("Ask!", variant="primary")

    def respond(message, chat_history):
        response = send_query(message)
        chat_history.append((message, response))
        return chat_history, ""

    submit_btn.click(fn=respond, inputs=[input_box, chatbot], outputs=[chatbot, input_box])
    input_box.submit(fn=respond, inputs=[input_box, chatbot], outputs=[chatbot, input_box])


if __name__ == "__main__":
    print("Agent initialized. Check terminal for Gradio URL\n")
    iface.launch(share=True, debug=True)