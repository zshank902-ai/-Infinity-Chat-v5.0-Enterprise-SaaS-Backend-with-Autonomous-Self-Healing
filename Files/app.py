from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# A zero-token rule-based "AI" brain with keyword intelligence
AI_KB = {
    "hello": ["Hello there! How can I help you build something awesome today?", "Hi! What's on your mind?"],
    "help": ["I am a zero-token AI built to assist you. Try asking me about coding, life, or weather!"],
    "weather": ["I can't look outside, but I hope it's sunny where you are!"],
    "joke": [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "There are 10 types of people in the world: those who understand binary, and those who don't."
    ],
    "default": [
        "That's fascinating! Tell me more.",
        "I'm processing that with 100% organic, zero-token logic.",
        "Interesting point! Can you elaborate?"
    ]
}

def get_smart_response(user_message):
    msg = user_message.lower()
    for keyword in AI_KB:
        if keyword in msg and keyword != "default":
            return random.choice(AI_KB[keyword])
    return random.choice(AI_KB["default"])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    bot_reply = get_smart_response(user_msg)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)