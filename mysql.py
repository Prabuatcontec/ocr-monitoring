import MySQLdb
import json
from config import Config


class Connection:
    def __init__(self):
        self.db = MySQLdb.connect(
            Config.DATABASE_CONFIG['server'],
            Config.DATABASE_CONFIG['user'],
            Config.DATABASE_CONFIG['password'],
            Config.DATABASE_CONFIG['name']
        )
        self.db.autocommit(True)
        self.db.set_character_set('utf8mb4')
        self.cur = self.db.cursor()

    def getCustomer(self):
        self.cur.execute("select Id, Name from Customers")

        rows = [x for x in self.cur]
        cols = [x[0] for x in self.cur.fetchall()]
        customers = []
        for row in rows:
            customer = {}
            for prop, val in zip(cols, row):
                customer[prop] = val
            customers.append(customer)
        return customers

    def getModels(self, customer_id):
        self.cur.execute(
            "SELECT m.Name,m.Validation FROM Automation.CustomerModels  cm LEFT JOIN Automation.Models m ON cm.ModelId = m.Id Where cm.CustomerId =%d" % int(customer_id))

        rows = [x for x in self.cur]
        cols = [x[0] for x in self.cur.fetchall()]
        models = []

        for row in rows:
            model = {}
            v = 0
            for prop, val in zip(cols, row):
                v = v+1
                model[v] = val
            models.append(model)
        return models

    def insertModel(self, model, serial):
        mycursor = self.cur

        sql = "INSERT INTO Automation.ScannedSerials (Serials, model) VALUES (%s, %s)"
        val = (serial, model)
        self.cur.execute(sql, val)
 
        return 1
