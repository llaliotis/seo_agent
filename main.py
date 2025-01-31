from openai import OpenAI
import os
from dotenv import load_dotenv
from prompts import react_system_prompt
from json_helpers import extract_json
import requests
import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr

# Load environment variables
load_dotenv()

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# Create an instance of the OpenAI class
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_text_with_conversation(messages, model="gpt-3.5-turbo"):
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

def get_seo_page_report(url: str):
    api_url = "https://website-seo-analyzer.p.rapidapi.com/seo/seo-audit-basic"
    
    querystring = {"url": url}
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "website-seo-analyzer.p.rapidapi.com"
    }
    
    response = requests.get(api_url, headers=headers, params=querystring)
    
    return response.json()  # Return the JSON response

def on_submit():
    user_query = entry.get()
    if user_query:
        process_query(user_query)
    else:
        messagebox.showwarning("Warning", "Please enter a query.")

def listen_for_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    
    try:
        # Recognize speech using Google Speech Recognition
        user_query = recognizer.recognize_google(audio)
        entry.delete(0, tk.END)  # Clear any previous text in the entry
        entry.insert(0, user_query)  # Insert the recognized speech into the entry field
        process_query(user_query)
    except sr.UnknownValueError:
        messagebox.showerror("Error", "Could not understand audio")
    except sr.RequestError as e:
        messagebox.showerror("Error", f"Could not request results; {e}")

def process_query(user_query):
    messages = [
        {"role": "system", "content": react_system_prompt},
        {"role": "user", "content": user_query},
    ]

    turn_count = 1
    max_turns = 5

    while turn_count < max_turns:
        print(f"Loop: {turn_count}")
        print("----------------------")
        turn_count += 1

        response = generate_text_with_conversation(messages, model="gpt-4")

        print(response)

        json_function = extract_json(response)

        if json_function:
            function_name = json_function[0]['function_name']
            function_parms = json_function[0]['function_parms']
            
            if function_name not in available_actions:
                raise Exception(f"Unknown action: {function_name}: {function_parms}")
            
            print(f" -- running {function_name} {function_parms}")
            action_function = available_actions[function_name]
            
            # Call the function with parameters
            result = action_function(**function_parms)
            function_result_message = f"Action_Response: {result}"
            messages.append({"role": "user", "content": function_result_message})
            print(function_result_message)
        else:
            break

    # Display the final response in a message box
    messagebox.showinfo("Response", response)

# Update the available actions dictionary
available_actions = {
    "get_seo_page_report": get_seo_page_report
}

# Create main window
root = tk.Tk()
root.title("Query Interface")

# Create and place the text entry field
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# Create and place the submit button for text input
submit_button = tk.Button(root, text="Submit Query", command=on_submit)
submit_button.pack(pady=5)

# Create and place the button for voice input
voice_button = tk.Button(root, text="Voice Input", command=listen_for_voice)
voice_button.pack(pady=5)

# Start the GUI event loop
root.mainloop()