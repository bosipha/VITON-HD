from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Virtual Try-On is Running!"

if __name__ == "__main__":
    app.run(debug=True)
