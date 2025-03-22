from flask import Flask, render_template

app = Flask(__name__)

# Route to serve the main page
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve a simple message
@app.route('/api/message', methods=['GET'])
def get_message():
    # this is the comment line
    return "Hello from the back-end! This data was fetched when you clicked the button."

if __name__ == '__main__':
    app.run(debug=True)