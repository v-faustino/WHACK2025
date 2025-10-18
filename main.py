from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/business")
def business():
    return render_template("business.html")

@app.route("/employee")
def employee():
    return render_template("employee.html")

@app.route("/personal")
def personal():
    return render_template("personal.html")

@app.route("/vendors")
def vendors():
    return render_template("vendors.html")




if __name__ == "__main__":
    app.run(debug=True)