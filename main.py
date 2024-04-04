# (C) Copyright Peter Hinch 2017-2019.
# Released under the MIT licence.

# This demo publishes to topic "result" and also subscribes to that topic.
# This demonstrates bidirectional TLS communication.
# You can also run the following on a PC to verify:
# mosquitto_sub -h test.mosquitto.org -t result
# To get mosquitto_sub to use a secure connection use this, offered by @gmrza:
# mosquitto_sub -h <my local mosquitto server> -t result -u <username> -P <password> -p 8883

# Public brokers https://github.com/mqtt/mqtt.github.io/wiki/public_brokers

# red LED: ON == WiFi fail
# green LED heartbeat: demonstrates scheduler is running.

from mqtt_as import MQTTClient
from mqtt_local import config
import uasyncio as asyncio
import dht, machine
import json
import btree

d = dht.DHT22(machine.Pin(25))
a = []
setpoint = 0
periodo = 0
modo = 0


'''def sub_cb(topic, msg, retained):
    print('Topic = {} -> Valor = {}'.format(topic.decode(), msg.decode()))

async def wifi_han(state):
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe('24dcc399d76c/setpoint', 1)
    await client.subscribe('24dcc399d76c/periodo', 1)
    await client.subscribe('24dcc399d76c/destello', 1)
    await client.subscribe('24dcc399d76c/modo', 1)
    await client.subscribe('24dcc399d76c/rele', 1)'''

async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
        if (topic.decode() == '24dcc399d76c/setpoint'):
            print("anda")
            setpoint = msg.decode()
        

async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe('24dcc399d76c/setpoint', 1)
        await client.subscribe('24dcc399d76c/periodo', 1)
        await client.subscribe('24dcc399d76c/destello', 1)
        await client.subscribe('24dcc399d76c/modo', 1)
        await client.subscribe('24dcc399d76c/rele', 1)

async def main(client):
    await client.connect()
    n = 0
    await asyncio.sleep(2)  # Give broker time

    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))

    while True:
        try:
            d.measure()
            
            
            try:
                dato = {
                't':d.temperature(),
                'h':d.humidity(),
                's':setpoint,
                'p':periodo,
                'm':modo
                }
                b = json.dumps(dato)
                await client.publish('24dcc399d76c', '{}'.format(b), qos = 1)
            except OSError as e:
                print("sin sensor temperatura")
        except OSError as e:
            print("sin sensor")
        await asyncio.sleep(20)  # Broker is slow


'''
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
'''
config["queue_len"] = 1  # Use event interface with default queue size
MQTTClient.DEBUG = False  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors