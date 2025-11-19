from flask import Flask, jsonify, send_file
import io
import matplotlib.pyplot as plt
import numpy as np
import random

app = Flask(__name__, static_folder="static")

@app.route("/")
def front():
    return app.send_static_file("frontend.html")

@app.route("/graph")
def generate_graph():
    x = np.linspace(0, 2*np.pi, 200)
    y = np.sin(x) + np.random.normal(scale=0.1, size=x.shape)
    buf = io.BytesIO()
    plt.plot(x, y)
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype="image/png")

@app.route("/table")
def random_table():
    data = []
    for i in range(5):
        row = {"A": random.randint(1,100),
               "B": random.randint(1,100),
               "C": random.randint(1,100)}
        data.append(row)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
