import json
import btree

x = {
  "name": "John",
  "age": 30,
  "city": "New York"
}


# convert into JSON:
y = json.dumps(x)

# the result is a JSON string:
print(y)

try:
    f = open("mydb", "r+b")
except OSError:
    f = open("mydb", "w+b")

db = btree.open(f)

db["name"] = x["name"]
db["age"] = x["age"]
db["city"] = x["city"]

db.flush()
db.close()
f.close()

try:
    f = open("mydb", "r+b")
except OSError:
    f = open("mydb", "w+b")

db = btree.open(f)

for key in db:
    print(key)