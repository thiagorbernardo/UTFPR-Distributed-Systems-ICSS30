import json
import base64
import random
import threading
import time
from typing import List
import uuid
from datetime import datetime
import csv
import io
import Pyro5.api
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

class Manager:
    _id: str
    name: str
    public_key: Ed25519PublicKey
    notification_uri: str

    def __init__(self, name: str, public_key: bytes, notification_uri: str):
        self._id = str(uuid.uuid4())
        self.name = name
        bytes_data = base64.b64decode(public_key['data'])
        self.public_key = Ed25519PublicKey.from_public_bytes(bytes_data)
        self.notification_uri = notification_uri


    def verify_signature(self, signature: str):
        print('verify signature')
        signature_bytes = base64.b64decode(signature['data'])
        self.public_key.verify(signature_bytes, self.name.encode('utf-8'))

    def notify(self, type: int, message: str):
        manager_notifier = Pyro5.api.Proxy(self.notification_uri)
        manager_notifier.notify(type, message)
        

class Product:
    _id: str
    name: str
    description: str
    price: float
    quantity: int
    minQuantity: int

    def __init__(self, name: str, description: str, price: float, quantity: int, minQuantity: int):
        self._id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.minQuantity = minQuantity


class ProductHistory:
    _id: str
    productId: str
    quantity: int
    date: str

    def __init__(self, productId: str, quantity: int):
        self._id = str(uuid.uuid4())
        self.productId = productId
        self.quantity = quantity
        self.date = datetime.now().isoformat()#.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def save(self):
        history = []
        with open('history.json', 'r') as json_file:
            json_data = json_file.read()
            history = json.loads(json_data)

        history.append(self.__dict__)

        with open('history.json', 'w') as json_file:
            json_file.write(json.dumps(history))
        pass


class Stock:
    def __init__(self):
        print('init stock')
        self.stock: List[Product] = []
        self.refresh_stock()

    def refresh_stock(self):
        print('refresh stock')
        with open('stock.json', 'r') as json_file:
            json_data = json_file.read()
            self.stock = json.loads(json_data)

    def save_stock(self):
        print('save stock')
        with open('stock.json', 'w') as json_file:
            json_file.write(json.dumps(self.stock))

    def edit_stock(self, id: str, quantity: int):
        for item in self.stock:
            if item['_id'] == id:
                print(f'item: {item["_id"]} - current quantity: {item["quantity"]} - add {quantity} to current quantity')
                item['quantity'] += quantity
                ProductHistory(item['_id'], quantity).save()

        self.save_stock()
        self.refresh_stock()

    def add_stock(self, name: str, description: str, price: float, quantity: int, minQuantity: int):
        print('add stock')
        product = Product(name, description, price, quantity, minQuantity)
        self.stock.append(product.__dict__)
        self.save_stock()
        self.refresh_stock()

        return product._id

    def get_stock(self):
        return self.stock.copy()

    def get_stock_by_id(self, id: str):
        for item in self.stock:
            if item['_id'] == id:
                return item

        return None


class Report:
    type: int
    stock: Stock

    def __init__(self, type: int, stock: Stock):
        self.type = type
        self.stock = stock

    def get_report(self, date: datetime = None):
        report = []
        if self.type == 1:
            report = self.get_stock_report()
        elif self.type == 2:
            report = self.get_history_report()
        elif self.type == 3:
            report = self.get_low_interest_report(date)
        elif self.type == 4:
            report = self.get_low_stock_report()
        else:
            report = []

        return self.report_to_csv(report)

    def get_stock_report(self):
        return self.stock.get_stock()

    def get_history_report(self):
        history = []
        with open('history.json', 'r') as json_file:
            json_data = json_file.read()
            history = json.loads(json_data)

        return history

    def get_low_interest_report(self, date: datetime = None):
        history = self.get_history_report()
        stock = self.get_stock_report()
        low_interest = []

        history_product_ids = [item['productId'] for item in history if datetime.fromisoformat(item['date']) >= date and item['quantity'] > 0]
        history_product_ids_unique = list(set(history_product_ids))

        # print(history_product_ids_unique)

        for item in stock:
            if item['_id'] not in history_product_ids_unique:
                low_interest.append(item)

        # print(low_interest)
        return low_interest

    def get_low_stock_report(self):
        stock = self.get_stock_report()
        min_quantity_stock_items = []

        for item in stock:
            if item['quantity'] <= item['minQuantity']:
                min_quantity_stock_items.append(item)

        return min_quantity_stock_items

    def report_to_csv(self, report):
        if not report:
            return

        # Get the keys from the first dictionary in the list
        keys = report[0].keys()

        # Open a new CSV file for writing
        csv_file = io.StringIO()

        writer = csv.DictWriter(csv_file, fieldnames=keys)

        # Write the header row to the CSV file
        writer.writeheader()

        # Write each dictionary in the list as a row to the CSV file
        for row in report:
            writer.writerow(row)

        return csv_file.getvalue()


@Pyro5.api.expose
class Server:
    stock: Stock
    manager: Manager

    def __init__(self):
        self.stock = Stock()
        self.manager = None

    def add_manager(self, name: str, public_key: bytes, notification_uri: str):
        self.manager = Manager(name, public_key, notification_uri)
        threading.Thread(target=self._cron_notifications, args=()).start()

    def verify_manager(self, signature: str):
        if(self.manager == None):
            raise Exception('Manager not found')
        self.manager.verify_signature(signature)

        print('Manager verified')

    def add_product(self, name: str, description: str, price: float, quantity: int, minQuantity: int, signature: str):
        self.verify_manager(signature)
        self.stock.add_stock(name, description, price, quantity, minQuantity)

    def edit_product(self, id: str, quantity: int, signature: str):
        self.verify_manager(signature)
        self.stock.edit_stock(id, quantity)

    def get_report(self, type: int, date: datetime = None, signature: str = None):
        self.verify_manager(signature)
        report = Report(type, self.stock)
        if(date):
            date = datetime.fromisoformat(date)
        return report.get_report(date)

    def _cron_notifications(self):
        while not threading.Event().is_set():
            if(self.manager != None):
                low_intereset_report = Report(3, self.stock).get_report(datetime(1999, 1, 1))
                low_stock_report = Report(4, self.stock).get_report()
                if(low_intereset_report):
                    self.manager.notify(3, low_intereset_report)
                if(low_stock_report):
                    self.manager.notify(4, low_stock_report)
                print("enviando notificação \n")
                time.sleep(60)

if __name__ == '__main__':
    try:
        daemon = Pyro5.server.Daemon()         # make a Pyro daemon
        ns = Pyro5.api.locate_ns()             # find the name server
        uri = daemon.register(Server)   # register the greeting maker as a Pyro object
        ns.register("server.uri", uri)   # register the object with a name in the name server

        print("Ready.")
        daemon.requestLoop()                   # start the event loop of the server to wait for calls

    except Exception as e:
        print(f'Error {e}')
