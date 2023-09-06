import paho.mqtt.client as mqtt
import json

# Método é chamado quando a conexão é realizada
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Se inscreve no tópico especifico
    print("Inscrito no topico ELECTRONICS")
    client.subscribe("ELECTRONICS")
    print("Inscrito no topico HOUSEHOLD")
    client.subscribe("HOUSEHOLD")


# Método é chamado quando uma mensagem é recebida
def on_message(client, userdata, msg):
    # Tratamos o pacote recebido
    mensagem = json.loads(msg.payload.decode("utf-8","ignore"))
    # Escrevemos no terminal a mensagem recebida
    print("Teste, temos uma nova promocao de " + mensagem.get("category") + " nas lojas " + mensagem.get("store") + " por apenas " 
    + str(mensagem.get("price")) + " reais.")

# Inicia o MQTT Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()