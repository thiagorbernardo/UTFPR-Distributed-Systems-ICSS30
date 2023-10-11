import Pyro5.api
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import threading

class Client:
    
    name: str
    public_key: Ed25519PublicKey
    uri: str
    
    def __init__(self):
        self.name = None
        self.private_key = None
        self.public_key = None
        self.sign = None
        self.uri = None
        self.notify = Notify()
        self.server = None

    def firstRegister(self, name):
        self.name = name
        self.private_key = Ed25519PrivateKey.generate()
        self.sign = self.private_key.sign(bytes(name,'utf-8'))
        self.public_key = self.private_key.public_key()

        public_key_bytes = self.public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
        )

        print("\n")
        print(type(name))
        print(type(public_key_bytes))
        print(type(str(self.notify.uri)))
        print("\n")

        self.server = Pyro5.api.Proxy("PYRONAME:server.uri")
        self.server.add_manager(name, public_key_bytes, str(self.notify.uri))
        threading.Thread(target=self.wait_notification, args=()).start()

    def wait_notification(self):
        while not threading.Event().is_set():
            self.notify.daemon.requestLoop()

    
    def add_product(self):
        name = input("Digite o nome do produto: \n").strip()
        description = input("Digite a descrição do produto: \n").strip()
        price = input("Digite o preço do produto: \n").strip()
        quantity = input("Digite a quantidade do produto: \n").strip()
        minQuantity = input("Digite a quantidade minima do produto: \n").strip()
        self.server.add_product(name, description, float(price), int(quantity), int(minQuantity), self.sign)
        print("Produto adicionado com sucesso! \n")
        
    def edit_product(self):
        id = input("Digite o id do produto: \n").strip()
        quantidade = input("Digite a quantidade do produto (se for retirar digitar numero negativo): \n").strip()
        
        self.server.edit_product(id, int(quantidade), self.sign)
        print("Produto editado com sucesso! \n")

    def get_report(self):
        date = None
        print("Qual relatorio deseja gerar? \n 1) Relatorio de produtos em estoque \n 2) Relatorio de fluxo de movimentação \n 3) Relatorio de produtos sem saida por periodo")
        type = input("Digite qual relatorio deseja gerar: ")
        if int(type) == 3:
            date = input("Digite a data do relatorio (ano-mes-dia): ")
            date = date + "T00:00:00"
            date = datetime.fromisoformat(date)
    
        print(self.server.get_report(int(type), date, self.sign))

@Pyro5.api.expose
class Notify:

    def __init__(self):
        self.daemon = Pyro5.api.Daemon()
        self.uri = self.daemon.register(Notify)

    def notify(self, type: int, notify: str):

        print("Gerando relatorio \n\n")
        print(notify)


client = Client()
name = input("Primeiro registro, digite seu nome para vincula-lo com a uri e chaves\n").strip()
client.firstRegister(name)

while True:
    print("Qual função deseja realizar? \n 1) Adicionar um produto novo \n 2) Editar item \n 3) Gerar um relatorio \n 4) Quit")

    choice = input("Digite qual função deseja realizar: ")

    if choice == '1':
        client.add_product()
    elif choice == '2':
        client.edit_product()
    elif choice == '3':
        client.get_report()
    elif choice == '4':
        print("Adeus!")
        break
    else:
        print("Função inexistente digite. por facor digite uma opção valida")
    
    