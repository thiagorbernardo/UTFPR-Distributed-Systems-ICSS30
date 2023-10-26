import json
import base64
import threading
import time
from typing import List
import uuid
from datetime import datetime

from flask import Flask, request
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler
app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

class Manager:
    _id: str
    name: str

    def __init__(self, name: str):
        self._id = str(uuid.uuid4())
        self.name = name
        # self.notification_uri = notification_uri
        print(f'New Manager: {self.name} - {self._id}')# - {self.notification_uri}')

    def notify(self, type: int, message: str):
        # manager_notifier = Pyro5.api.Proxy(self.notification_uri)
        # manager_notifier.notify(type, message)
        # print(f'Notification({type}) sent to {self.notification_uri}')
        pass
        

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
        item_min_quantity = None
        for item in self.stock:
            if item['_id'] == id:
                print(f'item: {item["_id"]} - current quantity: {item["quantity"]} - add {quantity} to current quantity')
                item['quantity'] += quantity
                ProductHistory(item['_id'], quantity).save()
                if(item['quantity'] <= item['minQuantity']):
                    item_min_quantity = item

        self.save_stock()
        self.refresh_stock()
        return item_min_quantity

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
        if self.type == 1:
            return self.get_stock_report()
        elif self.type == 2:
            return self.get_history_report()
        elif self.type == 3:
            return self.get_low_interest_report(date)
        elif self.type == 4:
            return self.get_low_stock_report()
        else:
            return []

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

        history_product_ids = [item['productId'] for item in history if datetime.fromisoformat(item['date']) >= date and item['quantity'] < 0]
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

stock = Stock()
manager = None

def _verify_manager():
    if(manager == None):
        raise Exception('Manager not found')

    print('Manager verified')

def _cron_notifications():
    while not threading.Event().is_set():
        if(manager != None):
            low_intereset_report = Report(3, stock).get_report(datetime(1999, 1, 1))
            if(low_intereset_report):
                manager.notify(3, low_intereset_report)
            time.sleep(60)

@app.post('/manager')
def add_manager():
    global manager
    if not request.is_json: return {"error": "Request must be JSON"}, 415
    try:
        body = request.get_json()
        manager = Manager(body['name'])
        # threading.Thread(target=_cron_notifications, args=()).start()
        return {}, 201
    except Exception as e:
        print(f'Error {e}')
        return {"error": str(e)}, 500

@app.post('/products')
def add_product():
    if not request.is_json: return {"error": "Request must be JSON"}, 415
    try:
        _verify_manager()
        body = request.get_json()
        productId = stock.add_stock(body['name'], body['description'], body['price'], body['quantity'], body['minQuantity'])
        return {"id": productId}, 201
    except Exception as e:
        print(f'Error {e}')
        return {"error": str(e)}, 500

@app.patch('/products/<id>')
def edit_product(id: str):
    if not request.is_json: return {"error": "Request must be JSON"}, 415
    try:
        _verify_manager()
        body = request.get_json()
        item_min_quantity = stock.edit_stock(id, body['quantity'])
        if(item_min_quantity):
            manager.notify(4, json.dumps(item_min_quantity, indent=2))
        return {}, 200
    except Exception as e:
        print(f'Error {e}')
        return {"error": str(e)}, 500

@app.get('/reports/<int:type>')
def get_report(type: int):
    if type not in [1, 2, 3]: return {"error": "Invalid report type. Must be 1, 2 or 3"}, 400
    date = request.args.get('date')
    if type == 3 and date == None: return {"error": "Report 3 must have a ?date="}, 400
    try:
        _verify_manager()
        report = Report(type, stock)
        if(date):
            date = datetime.fromisoformat(date)
        return report.get_report(date), 200
    except Exception as e:
        print(f'Error {e}')
        return {"error": str(e)}, 500

@app.get('/')
def index():
    return 'Trabalho 4 de Sistemas Distribuídos - Estoque'