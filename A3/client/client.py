import Pyro5.api
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

class Client:
    def __init__(self):
        self.name = None
        self.private_key = None
        self.public_key = None
        self.sign = None
        self.uri = None
        self.notify = Notify()

    @Pyro5.api.expose
    def get_fortune(self, name):
        return "Hello, {0}. Here is your fortune message:\n" \
               "Behold the warranty -- the bold print giveth and the fine print taketh away.".format(name)

    def firstRegister(self, name):
        self.name = name
        self.private_key = Ed25519PrivateKey.generate()
        self.sign = self.private_key.sign(name.encode('utf-8'))
        self.public_key = self.private_key.public_key()

        server = Pyro5.api.Proxy("PYRONAME:server.uri")
        server.add_manager(name, str(self.public_key), self.notify.uri)

@Pyro5.api.expose
class Notify:

    def __init__(self):
        daemon = Pyro5.api.Daemon()
        self.uri = daemon.register(Notify)


client = Client()
print("Primeiro registro, digite seu nome para vincula-lo com a uri e chaves")
name = input()
client.firstRegister(name)

print("Qual função deseja realizar? \n 1) Editar item \n 2) Gerar relatorio")
    #SERVIÇO DE NOMES PARA FIRST COMUNICATION