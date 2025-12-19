import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import google.generativeai as genai

genai.configure(api_key="AIzaSyA9W_VITxQVSgWa_iJnosQ3GuyzF8FBtIQ")
def calculate():
    try:
        weight = float(weight_entry.get())
        height_cm = float(height_entry.get())
        age = int(age_entry.get())
        gender = gender_var.get()
        if weight <= 0 or height_cm <= 0 or (age <= 0 or age>=125) or gender not in ['Male', 'Female']:
            raise ValueError

        height_m = height_cm / 100.0
        bmi = weight / (height_m ** 2)
        bmi_value_label.config(text=f"{bmi:.1f}")
        category = get_bmi_category(bmi)
        category_label.config(text=category)

        bmr = calculate_bmr(weight, height_cm, age, gender)
        bmr_value_label.config(text=f"{bmr:.0f} kcal/day")

        colors = {
            "Underweight": "#ADD8E6",
            "Normal weight": "#90EE90",
            "Overweight": "#FFD580",
            "Obesity Class 1": "#FFCCCB",
            "Obesity Class 2": "#FF9999",
            "Obesity Class 3 (Severe)": "#E57373"
        }
        result_frame.config(bg=colors.get(category, result_bg_color))
        for lbl in result_labels:
            lbl.config(bg=colors.get(category, result_bg_color))

        chatbot_context['bmi_category'] = category
        add_chatbot_message(f"Your BMI category is '{category}'. Ask me any health-related question!")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid positive values for weight, height, age, and select your gender.")

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    elif bmi < 35:
        return "Obesity Class 1"
    elif bmi < 40:
        return "Obesity Class 2"
    else:
        return "Obesity Class 3 (Severe)"

def calculate_bmr(weight, height_cm, age, gender):
    if gender == 'Male':
        return 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height_cm - 5 * age - 161

def clear_fields():
    weight_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)
    age_entry.delete(0, tk.END)
    gender_var.set('Select')
    bmi_value_label.config(text="--")
    category_label.config(text="--")
    bmr_value_label.config(text="--")
    result_frame.config(bg=result_bg_color)
    for lbl in result_labels:
        lbl.config(bg=result_bg_color)
    chatbot_context['bmi_category'] = None
    chat_display.config(state='normal')
    chat_display.delete("1.0", tk.END)
    chat_display.config(state='disabled')
    add_chatbot_message("Chat reset. Calculate your BMI to start chatting.")

def add_chatbot_message(message):
    chat_display.config(state='normal')
    chat_display.insert(tk.END, "Bot: " + message + "\n\n")
    chat_display.config(state='disabled')
    chat_display.see(tk.END)

def user_send_message(event=None):
    msg = chat_entry.get().strip()
    if not msg:
        return
    chat_display.config(state='normal')
    chat_display.insert(tk.END, "You: " + msg + "\n")
    chat_display.config(state='disabled')
    chat_display.see(tk.END)
    chat_entry.delete(0, tk.END)
    add_chatbot_message("Thinking...")
    root.update_idletasks()

    bot_reply = chatbot_response(msg)
    chat_display.config(state='normal')
    chat_display.delete("end-3l", "end-1l") 
    add_chatbot_message(bot_reply)

def chatbot_response(user_msg):
    bmi_cat = chatbot_context.get('bmi_category')
    if not bmi_cat:
        return "Please calculate your BMI first to receive personalized health advice."

    prompt = f"""You are a health chatbot. The user's BMI category is '{bmi_cat}'.
User asks: "{user_msg}"
Please provide a helpful, informative and crisp response tailored to this health context."""

    try:
        gemini_model = genai.GenerativeModel("gemini-2.5-flash") 
        chat = gemini_model.start_chat(history=[])
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error contacting Gemini AI service: {e}"


root = tk.Tk()
root.title("BMI, BMR & Gemini AI Chatbot")
root.geometry("1100x900")
root.configure(bg="#1E1E2F")

result_bg_color = "#3B3B58"

top_frame = tk.Frame(root, bg="#1E1E2F")
top_frame.pack(side="top", fill="x", padx=15, pady=10)

input_frame = tk.Frame(top_frame, bg="#2D2D44", bd=2, relief="ridge")
input_frame.pack(side="left", padx=10, pady=10, fill="y")

def create_label_entry(parent, text, row):
    label = tk.Label(parent, text=text, font=("Helvetica", 14), fg="#FFFFFF", bg="#2D2D44")
    label.grid(row=row, column=0, padx=10, pady=8, sticky="w")
    entry = tk.Entry(parent, font=("Helvetica", 14), width=10, bg="#FFFFFF")
    entry.grid(row=row, column=1, padx=10, pady=8)
    return entry

weight_entry = create_label_entry(input_frame, "Weight (kg):", 0)
height_entry = create_label_entry(input_frame, "Height (cm):", 1)
age_entry = create_label_entry(input_frame, "Age (years):", 2)

gender_label = tk.Label(input_frame, text="Gender:", font=("Helvetica", 14), fg="#FFFFFF", bg="#2D2D44")
gender_label.grid(row=3, column=0, padx=10, pady=8, sticky="w")

gender_var = tk.StringVar(value='Select')
gender_dropdown = ttk.Combobox(input_frame, textvariable=gender_var, state="readonly", width=12, font=("Helvetica", 14))
gender_dropdown['values'] = ("Male", "Female")
gender_dropdown.grid(row=3, column=1, padx=10, pady=8)

button_frame = tk.Frame(input_frame, bg="#2D2D44")
button_frame.grid(row=4, column=0, columnspan=2, pady=12)

calculate_button = tk.Button(
    button_frame,
    text="Calculate",
    font=("Helvetica", 14, "bold"),
    bg="#FFD600", fg="#000",
    activebackground="#FFE066", activeforeground="#000",
    padx=10, command=calculate
)
calculate_button.grid(row=0, column=0, padx=10)

clear_button = tk.Button(
    button_frame,
    text="Clear",
    font=("Helvetica", 14,'bold'),
    bg="#8e24aa", fg="#000",
    activebackground="#CE93D8", activeforeground="#000",
    padx=10, command=clear_fields
)
clear_button.grid(row=0, column=1, padx=10)

result_frame = tk.Frame(top_frame, bg=result_bg_color, bd=2, relief="ridge")
result_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

bmi_text_label = tk.Label(result_frame, text="Your BMI:", font=("Helvetica", 14, "bold"), fg="#FFFFFF", bg=result_bg_color)
bmi_text_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

bmi_value_label = tk.Label(result_frame, text="--", font=("Helvetica", 14, "bold"), fg="#FFFFFF", bg=result_bg_color)
bmi_value_label.grid(row=0, column=1, padx=10, pady=8, sticky="w")

category_text_label = tk.Label(result_frame, text="Category:", font=("Helvetica", 14, "bold"), fg="#FFFFFF", bg=result_bg_color)
category_text_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")

category_label = tk.Label(result_frame, text="--", font=("Helvetica", 14,'bold'), fg="#FFFFFF", bg=result_bg_color)
category_label.grid(row=1, column=1, padx=10, pady=8, sticky="w")

bmr_text_label = tk.Label(result_frame, text="Your BMR:", font=("Helvetica", 14, "bold"), fg="#FFFFFF", bg=result_bg_color)
bmr_text_label.grid(row=2, column=0, padx=10, pady=8, sticky="w")

bmr_value_label = tk.Label(result_frame, text="--", font=("Helvetica", 14, "bold"), fg="#FFFFFF", bg=result_bg_color)
bmr_value_label.grid(row=2, column=1, padx=10, pady=8, sticky="w")

result_labels = [bmi_text_label, bmi_value_label, category_text_label, category_label, bmr_text_label, bmr_value_label]



bmi_classes = [
    ("Underweight", "< 18.5"),
    ("Normal weight", "18.5 – 24.9"),
    ("Overweight", "25 – 29.9"),
    ("Obesity Class 1", "30 – 34.9"),
    ("Obesity Class 2", "35 – 39.9"),
    ("Obesity Class 3 (Severe)", "40 and above"),
]

table_frame = tk.Frame(root, bg="#23233A")
table_frame.pack(side="top", padx=20, pady=5, fill="x")

table_label = tk.Label(table_frame, text="BMI Classification Table", font=("Helvetica", 15, "bold"), fg="#FFFFFF", bg="#23233A")
table_label.pack(anchor="w", padx=8, pady=(4, 4))

columns = ("Category", "BMI Range")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
tree.heading("Category", text="Category")
tree.heading("BMI Range", text="BMI Range")
tree.column("Category", width=200, anchor="center")
tree.column("BMI Range", width=130, anchor="center")

for category, bmi_range in bmi_classes:
    tree.insert("", "end", values=(category, bmi_range))

tree.pack(fill="x", padx=8, pady=6)

chatbot_frame = tk.Frame(root, bg="#2D2D44", bd=2, relief="ridge")
chatbot_frame.pack(side="right", padx=15, pady=10, fill="both", expand=True)

chat_label = tk.Label(chatbot_frame, text="Health Chatbot - Ask about your BMI", font=("Helvetica", 14, "bold"), fg="#FFFFFF", bg="#2D2D44")
chat_label.pack(anchor="n", pady=(10,5))

chat_display = tk.Text(chatbot_frame, height=20, bg="#23233A", fg="#FFFFFF", font=("Helvetica", 14), state="disabled", wrap="word")
chat_display.pack(padx=10, pady=(0,5), fill="both", expand=True)

chat_entry = tk.Entry(chatbot_frame, font=("Helvetica", 14))
chat_entry.pack(padx=10, pady=5, fill="x")
chat_entry.bind("<Return>", user_send_message)

send_button = tk.Button(chatbot_frame, text="Send", font=("Helvetica", 14, "bold"), bg="#FFD600", fg="#000",
                        activebackground="#FFE066", activeforeground="#000", command=user_send_message)
send_button.pack(padx=10, pady=(0,10))

chatbot_context = {'bmi_category': None}
add_chatbot_message("Welcome! Calculate your BMI first, then ask me about health advice!.")

root.mainloop()
