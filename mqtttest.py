import paho.mqtt.client as mqtt

# https://www.waveshare.com/wiki/Template:Raspberry_Pi_Guides_for_SPI_e-Paper

# The callback for when the client receives a CONNACK response from the server.


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("dabs")

# The callback for when a PUBLISH message is received from the server.


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


# https://github.com/eclipse/paho.mqtt.python
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("paper-dash", password="paper-dash")

client.connect("192.168.1.205", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

# paper-dash
