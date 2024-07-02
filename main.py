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
from machine import Pin

d = dht.DHT22(machine.Pin(25))
led = Pin(2, Pin.OUT)


async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
        if (topic.decode() == 'led'):
            if (msg.decode()):
                led.value(True)
            else:
                led.value(True)
        

async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe('led', 1)

async def main(client):
    await client.connect()
    n = 0
    await asyncio.sleep(2)  # Give broker time
    for coroutine in (up, messages):
        asyncio.create_task(coroutine(client))
    while True:
        try:
            a = led.value()
            await client.publish('led2', a, qos = 1)
        except OSError as e:
            print("sin sensor")
        await asyncio.sleep(20)  # Broker is slow



config["queue_len"] = 1  # Use event interface with default queue size
MQTTClient.DEBUG = False  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors