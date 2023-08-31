# Avaliação 1 - Seminários de Modelos de Computação Distribuída

Cada aluno(a) ou dupla de alunos(as) deve preparar uma apresentação (slides) de no máximo 15 minutos para explicar para a turma sobre um dos temas relacionados abaixo. Os slides devem ser entregues aqui na atividade até às 15h40 do dia 24/08/2023.
Temas:
Microsserviços;
Saga (orquestração e coreografia);
EDA (Event-Driven Architecture);
Kafka;
Amazon SQS (Simple Queue Service);
Amazon SNS (Simple Notification Service);
RabbitMQ e AMQP (Advanced Message Queuing Protocol);
ActiveMQ e JMS (Java Message Service);
Mosquitto e MQTT (Message Queuing Telemetry Transport);
Web Sockets;
SSE (Server-Sent Events);
Fediverse e Activity Pub;
Modelos de consistência centrados em dados.
Técnicas de controle de concorrência.


# Avaliação 2 - Arquitetura Orientada a Eventos

Desenvolvam uma aplicação, em qualquer linguagem de programação, em que ocorram eventos que sejam de interesse de outros processos. 
Escolham um serviço de mensageria (message broker) e um protocolo específico para comunicação baseada em mensagens. 
Criem dois ou mais tópicos nesse broker.
Três ou mais clientes assinantes vão registrar interesse em receber notificações de eventos publicados nos tópicos de seu interesse.
Dois ou mais clientes geradores de eventos vão publicar mensagens no broker.
Broker vai notificar os clientes assinantes interessados nos tópicos nos quais eles se registraram. 
Expliquem todo o funcionamento.

Quem quiser utilizar o RabbitMQ e AMQP, pode utilizar o tutorial abaixo disponível para várias linguagens:
https://www.rabbitmq.com/tutorials/tutorial-one-python.html
https://www.rabbitmq.com/tutorials/tutorial-one-java.html
https://www.rabbitmq.com/tutorials/tutorial-one-spring-amqp.html
https://www.rabbitmq.com/tutorials/tutorial-one-ruby.html
https://www.rabbitmq.com/tutorials/tutorial-one-php.html
entre outras
Obs.: vejam os tutoriais 1, 4 e 5.