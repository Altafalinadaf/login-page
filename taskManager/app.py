from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    tasks= ['buy milk','buy laptop']
    return render_template('index.html',tasks=tasks)

if __name__ =='__main__':
    app.run(debug=True)