import requests

url = "http://127.0.0.1:8000/ask"
data = {"question": "What is cognitive behavioral therapy?"}

with requests.post(url, json=data, stream=True) as response:
    for chunk in response.iter_lines():
        print(chunk.decode("utf-8"))  # Prints response in real time
