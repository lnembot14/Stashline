import requests

drake_dict = {"name": "Drake", "user_id": "lnembot14"}

response = requests.post(url="http://127.0.0.1:5000/artists", json= drake_dict)

print(response.status_code)
print(response.json())