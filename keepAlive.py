import time
import requests

URL = "https://dcschedul.onrender.com/"

while True:
    try:
        r = requests.get(URL, timeout=10)
        print("Ping success:", r.status_code)
    except Exception as e:
        print("Ping failed:", e)

    time.sleep(300)  # 300 秒 = 5 分鐘
