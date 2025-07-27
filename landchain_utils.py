import json
import os

USERS_FILE = "data/users.json"
TRANSFERS_FILE = "data/transfer_requests.json"

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def validate_user(username, password):
    users = load_json(USERS_FILE)
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False

def get_user_role(username):
    users = load_json(USERS_FILE)
    for user in users:
        if user["username"] == username:
            return user.get("role", "user")
    return "user"

def add_transfer_request(land_id, requester):
    requests = load_json(TRANSFERS_FILE)
    requests.append({ "land_id": land_id, "from": requester })
    save_json(TRANSFERS_FILE, requests)

def get_transfer_requests_for_owner(owner):
    requests = load_json(TRANSFERS_FILE)
    return [r for r in requests if r["land_id"].startswith(owner[:3])]  # Or another logic

def approve_transfer(land_id):
    from blockchain import Blockchain
    chain = Blockchain.from_file("data/land_records.json")
    for block in reversed(chain.chain):
        if block.data.get("land_id") == land_id:
            block.data["owner"] = "NEW_OWNER"  # You can add logic to get actual requester
            save_json("data/land_records.json", chain.to_dict())
            break

    # Remove request
    requests = load_json(TRANSFERS_FILE)
    requests = [r for r in requests if r["land_id"] != land_id]
    save_json(TRANSFERS_FILE, requests)

def mark_gst_paid(land_id):
    from blockchain import Blockchain
    chain = Blockchain.from_file("data/land_records.json")
    updated = False
    for block in chain.chain:
        if block.data.get("land_id") == land_id:
            if not block.data.get("gst_paid"):
                block.data["gst_paid"] = True
                updated = True
            break
    if updated:
        save_json("data/land_records.json", chain.to_dict())
    return updated
