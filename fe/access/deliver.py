import requests
from urllib.parse import urljoin


class Deliver:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "deliver/")

    def receive_books(self, user_id: str, order_id: str) -> (int,str):
        json = {"user_id": user_id, "order_id": order_id}
        url = urljoin(self.url_prefix, "receive_books")
        r = requests.post(url, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")

    def send_books(self, store_id: str, order_id: str) -> (int,str):
        json = {"store_id": store_id, "order_id": order_id}
        url = urljoin(self.url_prefix, "send_books")
        r = requests.post(url, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")
