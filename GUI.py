import tkinter as tk
from tkinter import messagebox
from LLM import LLM, read_prompt
import time


# Initialize the prompt
prompt = ("You are an AI assistant. You are tasked with answering questions from users. You should provide accurate "
          "and helpful responses to the best of your ability. If you are unsure about a question, you can ask for "
          "clarification. Your goal is to assist users and provide a positive experience.")

# Initialize the log file
# get the current time
current_time = time.strftime(f"%Y-%m-%d-%H-%M-%S", time.localtime())
with open(f"logs/{current_time}-log.txt", "a", encoding='utf-8') as f:
    f.write(f"Log file created at {current_time}\n")


# Answer the question
def query(question):
    # Create an instance of the Large Language Model
    llm = LLM(prompt=prompt)
    try:
        response = llm.query(question)
        res = f"{response}"
    except Exception as e:
        res = f"Error: '{e}'"
    # log file
    with open(f"logs/{current_time}-log.txt", "a", encoding='utf-8') as f:
        f.write(f"\n{current_time}: \nQ:\n{question}\n -> \nA:\n{res}\n\n")
    return res


# Custom prompt configuration
def update_prompt(prompt_content):
    global prompt
    prompt = prompt_content
    response_label.config(text=f"Prompt updated.")
    messagebox.showinfo("Success", "Prompt updated.")


# Function to handle the submission of the question
def submit_question():
    question = question_entry.get()
    if question:
        # Get the response from the query function
        response = query(question)
        # response = "Response: 'This is a mock response.'"
        # Display the response in the response label
        response_label.config(text=response)
        # Show success message popup
        messagebox.showinfo("Success", "Submit success")
    else:
        response_label.config(text="Please enter a question.")


# Language check function
def language_check(sentence):
    import language_tool_python as languagetool

    tool = languagetool.LanguageTool("en-US")
    matches = tool.check(sentence)

    if not matches:
        messagebox.showinfo("Success", "No language errors.")
        language_check_label.config(text="No language errors.")
    else:
        messagebox.showinfo("Language Errors", "Language errors found.")
        errors = [match for match in matches]
        language_check_label.config(text=f"Language errors found: {errors}")


# Initialize the main window
root = tk.Tk()
root.title("Chatbot")
root.geometry("500x500")

# Question Input
question_frame = tk.Frame(root)
question_frame.pack(pady=20)

question_label = tk.Label(question_frame, text="Input your question here")
question_label.pack()
question_entry = tk.Entry(question_frame, width=50)
question_entry.pack(pady=5)

# Submit Button
submit_button = tk.Button(root, text="Submit", command=submit_question)
submit_button.pack()

# Language check button
language_check_button = tk.Button(root, text="Check Language", command=lambda: language_check(question_entry.get()))
language_check_button.pack()
# Display the language check result
language_check_label = tk.Label(root, text="Language check result")
language_check_label.pack()

# Response Display
response_frame = tk.Frame(root)
response_frame.pack(pady=20)

response_label = tk.Label(response_frame, text="Show the response of the large language model", width=50, height=10,
                          relief="solid", anchor="nw", justify="left", wraplength=400)
response_label.pack()

# Start the GUI loop
root.mainloop()
