from openai import OpenAI
client = OpenAI(
    api_key="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"
)
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[     
        {"role": "user", "content": "You are a virtual assistent named jarvis skilled in general tasks like alexa and google"},
        {"role": "user", "content": "what is coding"}
    ]
)

print(completion.choices[0].message.content)