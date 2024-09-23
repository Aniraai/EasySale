import time
import gradio as gr
from util.prompt_util import *
from util.util import get_voice
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()  # This loads environment variables from a .env file

client_open_ai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def speech_to_text(audio_rec: bytes, language: str) -> str:
    language_map = {"English": "en", "Hindi": "hi", "Tamil": "ta", "Telugu": "te"}
    lang_code = language_map.get(language, "en")
    try:
        with open(audio_rec, "rb") as audio_file:
            transcript = client_open_ai.audio.transcriptions.create(
                model="whisper-1", file=audio_file, language=lang_code, response_format="text"
            )
        return transcript
    except Exception as e:
        print(e)
        return "Sorry, I did not get that."

def clear(messages: list, history: list) -> None:
    messages.clear()
    history.clear()

def add_text(history, messages, text, system_prompt, max_price, min_price, max_discount, min_discount, radio_training_focus, product_info):
    if history is None:
        history = []
    if messages is None:
        messages = []

    if len(messages) <= 1 or len(history) <= 1:
        product_prompt, diff_prompt = generate_product_prompt(max_price, min_price, max_discount, min_discount, radio_training_focus, product_info)
        if len(system_prompt) < 5:
            system_prompt = system_prompt_default

        messages = [{"role": 'system', 'content': system_prompt + diff_prompt + "\n" + prompt + product_prompt}]
        messages.append({"role": 'user', 'content': text})
        history.append((text, ''))
    else:
        messages.append({"role": 'assistant', 'content': history[-1][1]})
        messages.append({"role": 'user', 'content': text})
        history.append((text, ''))
    return history, messages, ""

def generate_response(history: list, messages: list, gender: str) -> tuple:
    start = time.time()
    flag = True
    voice_name = get_voice(gender=gender)
    sentence_tts = ""

    voice_stream = client_open_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )

    for chunk in voice_stream:
        if not chunk.choices or chunk.choices[0].delta.content is None:
            continue
        else:
            sentence_tts += chunk.choices[0].delta.content
            last_message = history[-1]
            history[-1] = (last_message[0], last_message[1] + chunk.choices[0].delta.content)

            if check_in_sentence(sentence_tts):
                response = client_open_ai.audio.speech.create(
                    model="tts-1",
                    voice=voice_name,
                    input=sentence_tts.strip(),
                )

                sentence_tts = ""
                yield history, response.content

def check_in_sentence(sentence):
    return any(char in sentence for char in ['.', '?', '!', ';', ":"])

# Main Gradio block for UI
with gr.Blocks() as demo:
    messages = gr.State(value=[])  # Store the messages between the user and the assistant
    history = gr.State(value=[])

    # Language dropdown
    language_dropdown = gr.Dropdown(
        label="Select Language",
        choices=["English", "Hindi", "Tamil", "Telugu"],  # Added Telugu
        value="English"  # Default language
    )

    with gr.Accordion(label="Set up scenario", open=False):
        dropdown = gr.Dropdown(label="Choose from curated role and scenario",
                               choices=dictv,
                               type="value",
                               value="Smith Urology Center")
        prompt_2 = gr.Textbox(value=system_prompt_default,
                              label="Input Scenario",
                              lines=8)

    with gr.Accordion(label="Set up product knowledge and rep training focus area",
                      open=False):
        max_price = gr.Textbox(label="Input Max Price (in USD)",
                               show_label=True,
                               placeholder="Input Maximum Price per unit(in USD)",
                               lines=1,
                               scale=1,
                               value=500)
        min_price = gr.Textbox(label="Input Min Price (in USD)",
                               show_label=True,
                               placeholder="Input Minimum Price per unit(in USD)",
                               lines=1,
                               scale=1,
                               value=5)
        max_discount = gr.Textbox(label="Input Max discount(in %)",
                                  show_label=True,
                                  placeholder="Input Max discount(in %)",
                                  lines=1,
                                  scale=1,
                                  value=100)
        min_discount = gr.Textbox(label="Input Min discount(in %)",
                                  show_label=True,
                                  placeholder="Input Min discount(in %)",
                                  lines=1,
                                  scale=1,
                                  value=1)
        product_info = gr.Textbox(label="Input product features (separated by newline)",
                                  show_label=True,
                                  placeholder="Input product features (separated by newline)",
                                  lines=4,
                                  scale=1,
                                  info="This helps in testing sales rep product knowledge",
                                  value="Multiple patents")
        radio_training_focus = gr.Radio(choices=["Objection Handling", "Negotiation", "Product Knowledge", "Overall"],
                                        value="Overall", label="Training Focus", type="value",
                                        info="Training focus for a sales rep.", interactive=True)

    with gr.Accordion(label="Set up persona", open=False):
        with gr.Row(equal_height=True):
            with gr.Column():
                radio_gender = gr.Radio(choices=["Female", "Male"], value="Female", label="Gender", type="value",
                                        info="Choose gender of buyer", interactive=True)

    chatbot = gr.Chatbot(value=[], elem_id="chatbot", height=300, label="AI Sales Coaching")

    with gr.Row(equal_height=True, visible=True):
        with gr.Column(scale=2):
            audio_input = gr.Audio(type="filepath", label='Audio Input', format="mp3", visible=True, scale=1)
            txt = gr.Textbox(label="User Input",
                             show_label=True,
                             placeholder="Enter text and press return",
                             lines=1,
                             scale=2,
                             visible=False)
        with gr.Column():
            audio_output = gr.Audio(
                streaming=True, container=True, label='Audio Response', autoplay=True, visible=False, scale=1)

            clear_btn = gr.ClearButton(components=[chatbot, audio_output], scale=2)
            clear_btn.click(clear, [messages, history], [])

        audio_input.stop_recording(
            speech_to_text,
            inputs=[audio_input, language_dropdown],
            outputs=[txt]
        ).then(
            add_text,
            inputs=[
                chatbot,
                messages,
                txt,
                prompt_2,
                max_price,
                min_price,
                max_discount,
                min_discount,
                radio_training_focus,
                product_info
            ],
            outputs=[
                chatbot,
                messages,
                txt
            ],
            queue=False
        ).then(
            generate_response,
            inputs=[
                chatbot,
                messages,
                radio_gender
            ],
            outputs=[
                chatbot,
                audio_output
            ]
        )

        def reset_state():
            demo.clear()

        def get_text(value):
            return dictv[value]

        txt.submit(
            add_text,
            inputs=[
                chatbot,
                messages,
                txt,
                prompt_2,
                max_price,
                min_price,
                max_discount,
                min_discount,
                radio_training_focus,
                product_info
            ],
            outputs=[
                chatbot,
                messages,
                txt
            ],
            queue=False
        ).then(
            generate_response,
            inputs=[
                chatbot,
                messages,
                radio_gender
            ],
            outputs=[
                chatbot,
                audio_output
            ]
        ).then(
            lambda: None,
            None,
            audio_input
        )

        dropdown.change(
            get_text,
            [dropdown],
            [prompt_2]
        )

demo.queue()
demo.launch()
