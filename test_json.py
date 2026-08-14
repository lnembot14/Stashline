import requests
import uuid

random_id = str(uuid.uuid4())

artist_dict = {"name": "Drake", "user_id": "lnembot14"}
response = requests.post(url= "http://127.0.0.1:5000/artists", json=artist_dict)
payload = {
    "name": "CLB",
    "user_id": "lnembot14",
    "artist_id": response.json()["id"]
}
era_response = requests.post(url="http://127.0.0.1:5000/eras", json=payload)
track_dict = {"title": "Vital", "era_id": era_response.json()["id"], "user_id":"lnembot14", "notes": "Catchy song"}
track_response = requests.post(url="http://127.0.0.1:5000/track", json=track_dict)
source_dict = {"user_id": "lnembot14", "url": "https://youtu.be/KW9cWBahTnY?si=qkPVhVjj3gUNGZFv", "platform": "Youtube", "track_id": track_response.json()["id"]}
source_response = requests.post(url= "http://127.0.0.1:5000/sources", json=source_dict)

print(track_response.json()["id"])
print(source_response.text)
print(source_response.status_code)



