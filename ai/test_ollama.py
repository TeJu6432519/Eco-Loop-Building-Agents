from ollama import chat

response = chat(
    model="qwen2.5:7b",
    messages=[
        {
            "role": "user",
            "content": """
You are an HVAC controller.
Return ONLY JSON.

Indoor temperature: 28
Outdoor temperature: 35
Occupancy: 8

{
    "setpoint": 24,
    "occupancy": 8
}
"""
        }
    ]
)

print(response["message"]["content"])