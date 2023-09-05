import paho.mqtt.client as mqtt
import json

# Callback running on connection
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # After connection we subscribe to the "$SYS/#" topics (internal topics that will produce lot of data, perfect for our example)
    print("Inscrito no topico ELECTRONICS")
    client.subscribe("ELECTRONICS")
    print("Inscrito no topico HOUSEHOLD")
    client.subscribe("HOUSEHOLD")


# Callback running on new message
def on_message(client, userdata, msg):
    # We print each message received
    mensagem = json.loads(msg.payload.decode("utf-8","ignore"))
    
    print("Teste, temos uma nova promocao de " + mensagem.get("category") + " nas lojas " + mensagem.get("store") + " por apenas " 
    + str(mensagem.get("price")) + " reais.")

# Initiate the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()