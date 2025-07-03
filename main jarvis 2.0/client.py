from openai import OpenAI
client = OpenAI(
    api_key=
)
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[     
        {"role": "user", "content": "You are a virtual assistent named jarvis skilled in general tasks like alexa and google"},
        {"role": "user", "content": "what is coding"}
    ]
)

print(completion.choices[0].message.content)
