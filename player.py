import json
from os import path
import random
import math
from copy import deepcopy
from config import MERCHANDISE, MACHINECOST

class Player:
    # data = {
    #     "loans": [{"Name": "Bank", "Amount": 1000, "Interest": 0.05, "Payment Date": "01-01-2025", "Time Left": 12}],
    #     "machines": {"Amount": 13, "Resources": {"coca": (500, 2.99)}, "prevSales": {"coca": (200,2.99)},}
    # }

    data = {"loans": [], "machines": {"Amount": 0, "Resources": {}, "Previous Week": {}}}
    currentPrices = None

    def __init__(self, name, money):
        self.name = name
        self.data["money"] = money

        try:
            self.data = json.loads(self.getUserData())
        except:
            self.storeUserData()

    def getAmountMachines(self):
        self.data = json.loads(self.getUserData())
        return self.data["machines"]["Amount"]

    def getResources(self):
        self.data = json.loads(self.getUserData())
        
        return self.data["machines"]["Resources"]
    
    def addResources(self, name, amount, price):
        amount = int(amount)
        price = float(price)

        resources = self.getResources()

        if name in resources:
            val0 = resources[name][0] + amount
            val1 = resources[name][1]
        else:
            val0 = amount
            val1 = MERCHANDISE[name]

        resources[name] = [val0, val1]
        self.data = json.loads(self.getUserData())
        self.data["machines"]["Resources"] = resources
        self.storeUserData()

        self.addMoney(-price*amount)

    def editPrice(self, name, newPrice):
        resources = self.getResources()
        
        resources[name] = [resources[name][0], newPrice]
        self.data = json.loads(self.getUserData())
        self.data["machines"]["Resources"] = resources
        self.storeUserData()

    def addMachines(self, numberAdded):
        self.data = json.loads(self.getUserData())
        self.data["machines"]["Amount"] += int(numberAdded)
        self.storeUserData()

        self.addMoney(-MACHINECOST*numberAdded)

    # Returns Name : Current Sales Value
    def getCurrentPrices(self):
        if self.currentPrices is not None:
            return self.currentPrices

        output = MERCHANDISE
        for name in MERCHANDISE:
            output[name] = round((1 + ((random.random() - 0.5) * 3.5/5)) * (MERCHANDISE[name] * 3/4), 2)
        
        self.currentPrices = output
        return output

    def addMoney(self, amount):
        self.data = json.loads(self.getUserData())
        self.data["money"] += amount
        self.storeUserData()


    def getMoney(self):
        self.data = json.loads(self.getUserData())
        return self.data["money"]

    def addLoan(self, name, amount, interest):
        amount = int(amount)
        interest = float(interest)
        self.data = json.loads(self.getUserData())

        for loan in self.data["loans"]:
            if loan["Name"] == name:
                loan["Amount"] += amount
                break
        else:
            self.data["loans"].append({"Name": name, "Amount": amount, "Interest": interest, "Payment Date": 4, "Paid Minimum": False})
        
        self.storeUserData()

    def getLoans(self):
        self.data = json.loads(self.getUserData())
        return self.data["loans"]
    
    def getMachines(self):
        self.data = json.loads(self.getUserData())
        return self.data["machines"]

    def setMachines(self, machines):
        self.data = json.loads(self.getUserData())
        self.data["machines"] = machines
        self.storeUserData()

    def storeUserData(self):
        with open(path.join("data", f"{self.name}.json"), "w") as f:
            f.write(json.dumps(self.data))

    def getUserData(self):
        with open(path.join("data", f"{self.name}.json"), "r") as f:
            # Only 1 line so its fine
            for line in f:
                return line

    def forwardLoans(self):
        loans = self.getLoans()
        self.data = json.loads(self.getUserData())

        # Bad coding, ik ik

        status = "Normal"

        for i in range(len(loans)):
            loans[i]["Payment Date"] -= 1
            
            # If 4 weeks late, you lose!
            if (loans[i]["Payment Date"]) == -4:
                return "Game Over"      
            # If payment overdue, increase interest
            elif (loans[i]["Payment Date"]) <= -1:
                loans[i]["Interest"] += 0.02
                status = "Overdue" 

            # Apply interest monthly
            if (loans[i]["Payment Date"] == 0):
                loans[i]["Amount"] *= (1 + loans[i]["Interest"] / 12) 

                if loans[i]["Paid Minimum"]:
                    loans[i]["Payment Date"] += 4
                    loans[i]["Paid Minimum"] = False

            # Hard round here cuz i cba to find where to round in proper place
            loans[i]["Amount"] = round(loans[i]["Amount"], 2)
            loans[i]["Interest"] = round(loans[i]["Interest"], 2)

        self.data["loans"] = loans
        self.storeUserData()
        return status

    def sales(self):
        status = "Normal"
        machines = self.getMachines()
        numMachines = machines["Amount"]
        resources = machines["Resources"]

        if numMachines == 0:
            return "No Machines"

        # Visiblity with a random deviation of +- 20%
        vis = (1 + (random.random() - 0.5) / 2.5) * getVisibility(numMachines)
        vis = int(vis)

        # Factor variety in
        vis *= len(resources) / len(MERCHANDISE)

        prevWeek = {}
        copy = deepcopy(resources)

        print(resources)

        for name in copy:
            numberAvailable, cost = resources[name]
            numberAvailable = int(numberAvailable)
            cost = float(cost)

            roughSales = vis / len(resources)

            # Stinker line - sells the rough number of sales +- 0.2
            actualSales = int(purchaseChance(MERCHANDISE[name], cost) * (roughSales + random.randint(int(-0.2*roughSales), int(0.2*roughSales))))

            # Altho that could surpass the number available, so its limited to the availability
            sales = min(numberAvailable, actualSales)
            
            if actualSales > numberAvailable:
                status = "Not Enough Goods"
                del resources[name]
            else:
                resources[name] = numberAvailable - sales, cost

            moneh = round(cost * sales, 2)
            self.addMoney(moneh)

            prevWeek[name] = [sales, round(cost, 2)]

        machines["Resources"] = resources
        machines["Previous Week"] = prevWeek
        self.setMachines(machines)

        if len(resources) / len(MERCHANDISE) != 1:
            status = "Not Diverse"

        return status

    def getPrevWeekSales(self):
        machines = self.getMachines()
        return machines["Previous Week"]

    def payLoan(self, name, amount):
        amount = float(amount)
        self.data = json.loads(self.getUserData())

        totalMoney = 0
        for loan in self.data["loans"]:
            if loan["Name"] == name:
                if amount >= 0.5 * loan["Amount"]:
                    loan["Paid Minimum"] = True

                loan["Amount"] -= amount
                totalMoney += amount

                print(loan) 
                break

        print(self.data["loans"])

        # Should be fine cuz 1 should be 0 at a time?
        copy = deepcopy(self.data["loans"])
        for index, loan in enumerate(copy):
            if loan["Amount"] == 0:
                self.data["loans"].pop(index)

        self.storeUserData()
        self.addMoney(-totalMoney)

def purchaseChance(expectedPrice, setPrice):
    STEEPNESS = 1.3

    return 0.5 + (math.atan(-STEEPNESS * (setPrice - expectedPrice)) / math.pi)

def getVisibility(numMachines):
    VISPERMACHINE = 300

    return VISPERMACHINE*numMachines + 20 * (numMachines - 1) ** 2




