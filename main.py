from mqtt_as import MQTTClient, config
import asyncio
from settings import SSID, password, BROKER
import dht, machine
import json
from time import sleep
from machine import Pin

d = dht.DHT22(machine.Pin(25))
# Local configuration
config['server'] = BROKER  # Change to suit
config['ssid'] = SSID
config['wifi_pw'] = password

temperatura = 0
humedad = 0
setpoint = 0
periodo = 0
modo = 0
rele = 0
destello = 0

led = Pin(2, Pin.OUT)
pinRele = 0

x = {
  "temperatura": 0,
  "humedad": 0,
  "setpoint": 150,
  "periodo": 0,
  "modo": 0
}

async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        #print(f'Topic: "{topic.decode()}" Message: "{msg.decode()}" Retained: {retained}')
        if (topic.decode() == '24dcc399d76c/setpoint'):
            setpoint = float(msg.decode())
            print(setpoint)
            #x.update({"setpoint",setpoint})
            x["setpoint"] = setpoint
        if (topic.decode() == '24dcc399d76c/periodo'):
            periodo = float(msg.decode())
            x["periodo"] = periodo
            print(periodo)
            #x.update({"periodo",periodo})
        if (topic.decode() == '24dcc399d76c/modo'):
            modo = float(msg.decode())
            x["modo"] = modo
            print(setpmodooint)
            #x.update({"modo",modo})
        if (topic.decode() == '24dcc399d76c/rele'):
            rele = float(msg.decode())
            print(rele)
        if (topic.decode() == '24dcc399d76c/destello'):
            destello = float(msg.decode())
            print(destello)       

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
                x.update({"temperatura":d.temperature()})
                x.update({"humedad":d.humidity()})
                b = json.dumps(x)
                await client.publish('24dcc399d76c', '{}'.format(b), qos = 1)
                
                if (rele == 1):
                    pinRele = 1
                else:
                    if (x["temperatura"] > x["setpoint"]):
                        print("rele")
                
                if (destello == 1):
                    led.value(not led.value())
                    sleep(2)
                    led.value(not led.value())
                    destello = 0
                
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