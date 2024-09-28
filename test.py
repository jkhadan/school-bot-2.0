import json

from Client import Client

users = {}

testClient = Client()

with open("UserData.json", 'r') as f:
    users = json.load(f)

users["users"].append("hello")

print(users["users"])