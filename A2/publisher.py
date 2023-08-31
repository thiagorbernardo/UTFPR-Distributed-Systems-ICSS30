import json
import random
import paho.mqtt.client as mqtt

class Publisher:
    def __init__(self, name):
        self.name = name
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect('localhost', 1883, 60)

    def run(self, product):
        print(f'Publisher {self.name} is running...')
        self.product = product
        self.publish()
        self.close()

    def publish(self):
        message = json.dumps(self.product)
        topic = self.product.get('category')
        
        print(f'Publishing message: {message} on topic: {topic}')
        self.mqtt_client.publish(topic, message)

    def close(self):
        print(f'Publisher {self.name} is closing...')
        self.mqtt_client.disconnect()


if __name__ == '__main__':
    try:
        print('Getting product...')

        with open('promotions.json', 'r') as json_file:
            json_data = json_file.read()
            products = json.loads(json_data)
            product = random.choice(products)

        print(f"{product['name']} - {product['store']} - {product['category']}")

        publisher = Publisher(product['store'])
        publisher.run(product)
    except Exception as e:
        print(f'Error {e}')
