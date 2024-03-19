import dht, machine

d = dht.DHT22(machine.Pin(23))
d.measure()
d.temperature()
d.humidity()

temperatura=d.temperature()
print(f"la temperatura actual es de {temperatura} *C")

humedad=d.humidity()

print(f"la humedad actual es de {humedad} %")