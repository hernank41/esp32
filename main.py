from mqtt_as import MQTTClient, config
import asyncio
from settings import SSID, password, BROKER
import dht, machine
import json

d = dht.DHT22(machine.Pin(25))
# Local configuration
config['server'] = BROKER  # Change to suit
config['ssid'] = SSID
config['wifi_pw'] = password

setpoint = 0
periodo = 0
modo = 0

async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        #print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
        if (topic.decode() == '24dcc399d76c/setpoint'):
            setpoint = msg.decode()
            print("anda setpoint")
            print(setpoint)

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
        await asyncio.sleep(10) 

config["queue_len"] = 1  # Use event interface with default queue size
MQTTClient.DEBUG = False  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors