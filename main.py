from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = "helloworld"


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    user = request.form.get("username")
    if user == "":
        return render_template("login.html", text="No fields may be left empty.")

    session["user"] = user
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/", methods=["POST", "GET"])
def home():
    if not ("user" in session):
        return redirect(url_for("login"))
    

    if request.method == "GET":
        return render_template("index.html")

@app.route("/business", methods=["POST", "GET"])
def business():
    if not ("user" in session):
        return redirect(url_for("login"))
    

    return render_template("business.html")

@app.route("/employee", methods=["POST", "GET"])
def employee():
    if not ("user" in session):
        return redirect(url_for("login"))
    

    return render_template("employee.html")

@app.route("/personal", methods=["POST", "GET"])
def personal():
    if not ("user" in session):
        return redirect(url_for("login"))
    

    return render_template("personal.html")

@app.route("/vendors", methods=["POST", "GET"])
def vendors():
    if not ("user" in session):
        return redirect(url_for("login"))
    

    return render_template("vendors.html")


@app.route("/banks", methods=["POST", "GET"])
def banks():
    if not ("user" in session):
        return redirect(url_for("login"))
    

    if request.method == "GET":
        return redirect(url_for("login"))
    

    amount = request.form.get("amount")
    
    # no fields can be empty
    if amount == "":
        return render_template("banks.html", text="No fields may be left empty.")
    

    # loan approved 
    # add amoun to account 


    return render_template("banks.html", text2="Loan Approved.")

if __name__ == "__main__":
    app.run(debug=True)