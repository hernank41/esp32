from mqtt_as import MQTTClient
from mqtt_local import config
import uasyncio as asyncio
import dht, machine, json

d = dht.DHT22(machine.Pin(25))
x = {
  "temperatura": 0,
  "humedad": 0,
}
led = machine.Pin(2, machine.Pin.OUT)
led.value(False)

def sub_cb(topic, msg, retained):
    print('Topic = {} -> Valor = {}'.format(topic.decode(), msg.decode()))
    if (topic.decode() == '/sensores_remoto/24dcc399d76c/led'):
        led_valor = msg.decode()
        if(msg.decode() == 'true'):
            led.value(True)
        else:
            led.value(False)

async def wifi_han(state):
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe('/sensores_remoto/24dcc399d76c', 1)
    await client.subscribe('/sensores_remoto/24dcc399d76c/led', 1)



async def main(client):
    await client.connect()
    n = 0
    await asyncio.sleep(2)  # Give broker time
    while True:
        try:
            d.measure()
            try:
                x.update({"temperatura":d.temperature()})
                x.update({"humedad":d.humidity()})
                b = json.dumps(x)
                await client.publish('/sensores_remoto/24dcc399d76c', '{}'.format(b), qos = 1)
            except OSError as e:
                print("sin sensor humedad")
        except OSError as e:
            print("sin sensor")
        await asyncio.sleep(10)  # Broker is slow

# Define configuration
config['subs_cb'] = sub_cb
config['connect_coro'] = conn_han
config['wifi_coro'] = wifi_han
config['ssl'] = True

# Set up client
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()