from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """
You are an AI Tutor for Year 7 Science students.
Explain concepts in simple language.
Be encouraging and clear.
If a student asks for an answer, explain instead of giving direct answers.
"""

print("🤖 AI Tutor Bot")
print("Type 'exit' to quit.\n")

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

while True:
    user_input = input("Student: ")

    if user_input.lower() == "exit":
        print("Tutor: Goodbye! Keep learning 😊")
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    tutor_reply = response.choices[0].message.content
    print("Tutor:", tutor_reply)

    messages.append({"role": "assistant", "content": tutor_reply})
