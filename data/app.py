from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/api/messag', methods=['GET'])
def get_msg():
    return "hello from the backend"


if __name__=='__main__':
    app.run(debug=True)
