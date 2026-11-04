
import json
import urllib.request

url = "http://localhost:11434/api/chat"

# Conversation memory

messages = [
    {
        "role": "system",
        "content": """
You are MyOwnAI, a smart personal AI assistant.

IMPORTANT LANGUAGE RULES:

1. Always reply in the same language and writing style
   used by the user.

2. If the user writes Hindi in English letters
   (Hinglish), reply in Hinglish using English letters.

3. If the user writes in Hindi Devanagari,
   reply in Hindi Devanagari.

4. If the user writes in English,
   reply in English.

5. Do not translate the user's language unnecessarily.

6. Keep answers natural, friendly and conversational.

7. Understand spelling mistakes and informal words.

8. Never invent personal information about the user.
   Only use information provided in the conversation.

9. If you don't know an answer, honestly say so.
"""
    }
]

print("🤖 MyOwnAI Started With Nitin")
print("Type 'exit' to stop.\n")

while True:

    question = input("You: ")

    if question.lower() == "exit":
        print("MyOwnAI: Goodbye!")
        break

    messages.append({
        "role": "user",
        "content": question
    })

    data = {
        "model": "qwen2.5:1.5b",
        "messages": messages,
        "stream": False
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        response = urllib.request.urlopen(request)
        result = json.loads(
            response.read().decode("utf-8")
        )

        answer = result["message"]["content"]

        print("\nMyOwnAI:", answer, "\n")

        messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as error:
        print("Error:", error)
