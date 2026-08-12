import requests
import uuid

random_id = str(uuid.uuid4())

artist_dict = {"name": "Drake", "user_id": "lnembot14"}
response = requests.post(url= "http://127.0.0.1:5000/artists", json=artist_dict)

payload = {
    "name": "Test Era - Bad FK",
    "user_id": "lnembot14",
    "artist_id": response.json()["id"]
}

era_response = requests.post(url="http://127.0.0.1:5000/eras", json=payload)

print(response.json())
print(era_response.text)
print(era_response.status_code)



