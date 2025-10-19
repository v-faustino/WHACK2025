from flask import Flask, render_template, redirect, url_for, request, session, flash
from player import Player
from config import MERCHANDISE, BANKS, MACHINECOST, RUNNINGCOST

app = Flask(__name__)
app.secret_key = "helloworld"

# rn signifies the current time in weeks, beginning at week 1
rn = 1
gameOver = False

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    user = request.form.get("username")
    '''if user == "":
        return render_template("login.html", text="No fields may be left empty.")'''

    session["user"] = user

    global player
    player = Player(session["user"], 0) # Create player with no money

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/", methods=["POST", "GET"])
def home():
    if not ("user" in session):   
        return redirect(url_for("login"))
    

    if request.method == "GET":
        sold = player.getPrevWeekSales()
        totalAmount = sum(int(sold[item][0]) for item in sold)
        totalRev = sum(float(sold[item][1] * sold[item][0]) for item in sold)

        return render_template("index.html", money="{:.2f}".format(player.getMoney()), time=rn, sold=sold, amount=totalAmount, rev="{:.2f}".format(totalRev))

@app.route("/business", methods=["POST", "GET"])
def business():
    if not ("user" in session):
        return redirect(url_for("login"))
    
    if request.method == "GET":
        return render_template("business.html", money="{:.2f}".format(player.getMoney()), time=rn, machines=player.getAmountMachines(), cost="{:.2f}".format(MACHINECOST), resources=player.getResources(), runningCost=player.getAmountMachines() * RUNNINGCOST)

    # check empty
    if request.form.get("amountMachines") == "" or request.form.get("newPrice") == "":
        return render_template("business.html", money="{:.2f}".format(player.getMoney()), time=rn, machines=player.getAmountMachines(), cost=MACHINECOST, resources=player.getResources(), runningCost=player.getAmountMachines() * RUNNINGCOST, msg="Field cannot be empty")

    # add machines or add resources price
    if request.method == "POST":
        if (request.form.get("newPrice") is None):
            machines = int(request.form.get("amountMachines"))
            
            # check if you can afford 
            if (player.getMoney() - machines * MACHINECOST) < 0:
                msg = "You cannot afford that many vending machines"
            
            else:
                player.addMachines(machines)
                msg = f"Bought {machines} vending machines"
        
        else:
            item = request.form.get("item")
            price = request.form.get("newPrice")
            player.editPrice(item, price)
            msg = f"Updated price to {price}" 

        return render_template("business.html", money="{:.2f}".format(player.getMoney()), time=rn, machines=player.getAmountMachines(), cost=MACHINECOST, resources=player.getResources(), runningCost=player.getAmountMachines() * RUNNINGCOST, msg=msg)


@app.route("/employee", methods=["POST", "GET"])
def employee():
    if not ("user" in session):
        return redirect(url_for("login"))
    

    return render_template("employee.html", money="{:.2f}".format(player.getMoney()), time=rn)

@app.route("/personal", methods=["POST", "GET"])
def personal():
    if not ("user" in session):
        return redirect(url_for("login"))
    

    return render_template("personal.html", money="{:.2f}".format(player.getMoney()), time=rn)

@app.route("/vendors", methods=["POST", "GET"])
def vendors():
    if not ("user" in session):
        return redirect(url_for("login"))
    
    if request.method == "GET":
        return render_template("vendors.html", money="{:.2f}".format(player.getMoney()), time=rn, stock=MERCHANDISE, price=player.getCurrentPrices())
    

    name = request.form.get("name")
    amount = request.form.get("amountResources")
    price = float(request.form.get("price"))

    if amount == "":
        return render_template("vendors.html", money="{:.2f}".format(player.getMoney()), time=rn, stock=MERCHANDISE, price=player.getCurrentPrices(), msg="Fields cannot be left empty")

    amount = int(amount)

    # check if can afford
    if (player.getMoney() - amount * price) < 0:
        return render_template("vendors.html", money="{:.2f}".format(player.getMoney()), time=rn, stock=MERCHANDISE, price=player.getCurrentPrices(), msg="You cannot afford these resources")

    player.addResources(name, amount, price)

    return render_template("vendors.html", money="{:.2f}".format(player.getMoney()), time=rn, stock=MERCHANDISE, price=player.getCurrentPrices(), msg2="Successful purchase")


@app.route("/banks", methods=["POST", "GET"])
def banks():
    if not ("user" in session):
        return redirect(url_for("logout"))
    

    if request.method == "GET":
        return render_template("banks.html", loans=player.getLoans(), banks=BANKS, money="{:.2f}".format(player.getMoney()), time=rn)

    

    amount = request.form.get("amount")
    
    # no fields can be empty
    if amount == "":
        return render_template("banks.html", text="No fields may be left empty.", loans=player.getLoans(), banks=BANKS, money="{:.2f}".format(player.getMoney()), time=rn)
    

    # loan approved 
    # add amoun to account 
    player.addMoney(float(amount))
    
    bank = BANKS[int(request.form.get("index"))]

    interest = bank["Interest"]
    time = bank["Time"]
    name = bank["Name"]

    print(name, interest, time)

    # existingLoans = player.getLoans()

    player.addLoan(name, amount, interest, time, rn)
    print(player.getLoans())
    return render_template("banks.html", text2="Loan Approved.", loans=player.getLoans(), banks=BANKS, money="{:.2f}".format(player.getMoney()), time=rn)


@app.route("/advance", methods=["POST", "GET"])
def advanceTime():
    loanStatus = player.forwardLoans()
    saleStatus = player.sales()
    if loanStatus == "Game Over" or saleStatus == "Game Over": 
        flash("Unfortuntately you failed to pay credit in time. Game Over.", 'danger')

    else :
        global rn
        rn += 1

        player.currentPrices = None # Reset Current Prices, so new ones are generated next week
        
        totalRunningCost = player.getAmountMachines() * RUNNINGCOST
        if totalRunningCost > player.getMoney():
            moneh = player.getMoney()
            player.addMoney(-moneh) # Zero Money
            player.addLoan("Machine Maintenance", totalRunningCost - moneh, 0.30, 0, rn) # Add difference as a loan

            #TODO ADD MESSAGE ABOUT THIS
            flash("You didn't have enough money to run all your machines, emergency loan taken. PAY IMMEDIATELY!!!", 'danger')
            
            #TODO DISPLAY WEEKLY RUNNING COST IN BUSINESS TAB IG??? 

        else:
            player.addMoney(-totalRunningCost) # Every week, each machine costs some money

        # Overdue
        if loanStatus == "Overdue":
            flash("Payment for a loan was overdue, your interest has been increased.",'error')

        # Game Over
        elif loanStatus == "Game Over": 
            flash("Game Over. You missed too many payment dates.",'error')

        elif saleStatus == "Not Enough Goods":
            flash("You didn't have enough stock to satisfy all your customers.", 'warning')

        elif saleStatus == "Not Diverse":
            flash("You don't have enough unique items. Sales severely impacted.", 'warning')

        elif saleStatus == "No Machines": 
            flash("You didn't have any machines working.", 'warning')

        else:
            flash("1 week advanced, loans are normal.", 'success')



    return redirect(url_for("home"))


@app.route("/repay", methods=["POST", "GET"])
def repay():
    bank = request.form.get("bank")
    amount = request.form.get("repayAmount")
    msg = ""
    msg2 = ""
    if amount == "":
        msg = "Fields cannot be empty"

    if amount is None:
        msg = "Try again"

    elif float(amount) <= player.getMoney():
        player.payLoan(bank, amount)
        msg2 = "Payment made successfully"

    else:
        msg="You cannot afford to make this payment."

    return render_template("banks.html", msg=msg, msg2=msg2, loans=player.getLoans(), banks=BANKS, money="{:.2f}".format(player.getMoney()), time=rn)

if __name__ == "__main__":
    app.run(debug=True)