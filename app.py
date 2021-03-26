from datetime import datetime
import json

import db
from flask import Flask
from flask import request

DB = db.DatabaseDriver()

app = Flask(__name__)

def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(error, code=404):
    return json.dumps({"success": False, "error": error}), code


@app.route("/")
@app.route("/api/users/")
def get_all_users():
    data = DB.get_all_users()
    return success_response(data)

@app.route("/api/users/", methods = ["POST"])
def create_user():
    data = json.loads(request.data)
    name = data.get("name")
    username = data.get("username")
    balance = data.get("balance", 0)
    if not name or not username:
        return failure_response("Please include a name and/or username")
    user_id = DB.create_user(name, username, balance)
    user = DB.get_user_by_id(user_id)
    all = DB.get_all_transactions(user_id)
    lst = []
    for x in all:
        if x["sender_id"] == user_id or x["receiver_id"] == user_id:
            lst.append(x)
    user["transactions"] = lst
    return success_response(user)


@app.route("/api/user/<int:user_id>/")
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user:
        lst = []
        all = DB.get_all_transactions(user_id)
        for x in all:
            if x["sender_id"] == user_id or x["receiver_id"] == user_id:
                lst.append(x)
        user["transactions"] = lst
        return success_response(user)
    return failure_response("Enter correct user id")


@app.route("/api/user/<int:user_id>/", methods = ["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user:
        DB.delete_user(user_id)
        return success_response(user)
    return failure_response("That user does not exist")


@app.route("/api/transactions/", methods = ["POST"])
def create_transaction():
    data = json.loads(request.data)
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    amount = data.get("amount") 
    message = data.get("message")
    accepted = data.get("accepted")

    #verification
    if sender_id is None or receiver_id is None or amount is None or message is None:
        return failure_response("Incorrect input")
    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if not receiver or not sender:
        return failure_response("One of the users does not exist")
    timestmp = datetime.now()

    
    #accepted
    if accepted:
        sender_money = sender["balance"]
        receiver_money = receiver["balance"]
        if (sender_money - amount < 0):
            return failure_response("Insufficient funds")   
        DB.update_user_money(sender_id, sender_money - amount)
        DB.update_user_money(receiver_id, receiver_money + amount)

    #create id
    transaction_id = DB.create_transaction(timestmp, sender_id, receiver_id, amount, message, accepted)


    transaction = DB.get_transaction_by_id(transaction_id)
    return success_response(transaction)


@app.route("/api/transaction/<int:trxn_id>/", methods = ["POST"])
def create_status(trxn_id):
    transaction = DB.get_transaction_by_id(trxn_id)
    if transaction is None:
        return failure_response("Not a valid transaction")
    data = json.loads(request.data)
    accepted = data.get("accepted")

    current = transaction["accepted"]

    #not valid
    if current is not None:
        return failure_response("Cannot change field")

    sender_id = transaction["sender_id"]
    receiver_id = transaction["receiver_id"]
    amount = transaction["amount"]

    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)

    #accepted
    if current is None and accepted == True:
        sender_money = sender["balance"]
        receiver_money = receiver["balance"]
        if (sender_money - amount < 0):
            return failure_response("Insufficient funds")
            
        DB.update_user_money(sender_id, sender_money - amount)
        DB.update_user_money(receiver_id, receiver_money + amount)

        DB.update_user_transaction(trxn_id, accepted, datetime.now())
    
    #
    if current is None and accepted == False:
        DB.update_user_transaction(trxn_id, accepted, datetime.now())


    transaction = DB.get_transaction_by_id(trxn_id)
    return success_response(transaction)







# your routes here


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
