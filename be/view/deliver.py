from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import deliver
import json

bp_deliver = Blueprint("deliver", __name__, url_prefix="/deliver")


@bp_deliver.route("/receive_books", methods=["POST"])
def receive_books():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    D = deliver.Delivery()
    code, message = D.receive_books(user_id, order_id)
    return jsonify({"message": message}), code


@bp_deliver.route("/send_books", methods=["POST"])
def send_books():
    store_id: str = request.json.get("store_id")
    order_id: str = request.json.get("order_id")

    D = deliver.Delivery()
    code, message = D.send_books(store_id, order_id)

    return jsonify({"message": message}), code