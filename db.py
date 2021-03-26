import os
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_user_table()
        self.create_transactions_table()


    def create_user_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            print(e)

    
    def get_all_users(self):
        cursor = self.conn.execute(
            """
            SELECT * FROM users;
            """
        )
        users = []
        for user in cursor:
            users.append(
                {
                "id": user[0],
                "name": user[1],
                "username": user[2]
                }
            )
        return users


    def create_user(self, name, username, balance = 0):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (name, username, balance) VALUES (?, ?, ?);
            """,
            (name, username, balance)
        )
        self.conn.commit()
        return cursor.lastrowid

    
    def get_user_by_id(self, user_id):
        cursor = self.conn.execute(
            """
            SELECT * FROM users WHERE id = ?;
            """,
            (user_id,)
        )
        for user in cursor:
            return {
                "id": user[0],
                "name": user[1],
                "username": user[2],
                "balance": user[3]
            }
        return None 


    def delete_user(self, user_id):
        self.conn.execute(
            """
            DELETE FROM users WHERE id = ?;
            """,
            (user_id,)
        )  
        self.conn.commit()

    
    def update_user_money(self, id, balance):
        self.conn.execute(
            """
            UPDATE users SET balance = ? WHERE id = ?; 
            """,
            (balance, id)
        )
        self.conn.commit()

    
    def create_transactions_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestmp TIMESTAMP NOT NULL,
                    sender_id INTEGER SECONDARY KEY NOT NULL,
                    receiver_id INTEGER SECONDARY KEY NOT NULL,
                    amount INTEGER NOT NULL,
                    messge TEXT NOT NULL,
                    accepted INTEGER
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            print(e)


    def create_transaction(self, timestmp, sender_id, receiver_id, amount, messge, accepted):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO transactions (timestmp, sender_id, receiver_id, amount, messge, accepted) VALUES (?, ?, ?, ?, ?, ?);
            """,
            (timestmp, sender_id, receiver_id, amount, messge, accepted)
        )
        self.conn.commit()
        return cursor.lastrowid


    def update_user_transaction(self, id, accepted, timestmp):
        self.conn.execute(
            """ 
            UPDATE transactions SET accepted = ?, timestmp = ? WHERE id = ?;
            """,
            (accepted, timestmp, id)
        )
        self.conn.commit()

    
    def get_transaction_by_id(self, id):
        cursor = self.conn.execute(
            """
            SELECT * FROM transactions WHERE id = ?;
            """,
            (id,)
        )
        for trxn in cursor:
            return {
                "id": trxn[0],
                "timestamp": trxn[1],
                "sender_id": trxn[2],
                "receiver_id": trxn[3],
                "amount": trxn[4],
                "message": trxn[5],
                "accepted": trxn[6]
            }
        return None

    
    def get_all_transactions(self, user_id):
        cursor = self.conn.execute(
            """
            SELECT * 
            FROM transactions 
            INNER JOIN users
                ON transactions.receiver_id = users.id 
            -- WHERE 
            --    users.id = ? 
            ;
            """
            # (user_id,)
        )
        trxns = []
        for trxn in cursor:
            trxns.append(
                {
                "id": trxn[0],
                "timestamp": trxn[1],
                "sender_id": trxn[2],
                "receiver_id": trxn[3],
                "amount": trxn[4],
                "message": trxn[5],
                "accepted": trxn[6]
                }
            )
        return trxns
    



