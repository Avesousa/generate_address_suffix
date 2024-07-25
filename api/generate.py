import json
import os
import threading
import psycopg2
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from base58 import b58encode
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
stop_event = threading.Event()

app = Flask(__name__)
stop_event = threading.Event()

def generate_vanity_address(suffix: str):
    while not stop_event.is_set():
        keypair = Keypair()
        vanity_address = b58encode(str(keypair.pubkey())).decode('utf-8')
        secret = b58encode(keypair.secret()).decode('utf-8')
        # print(vanity_address)
        if vanity_address.endswith(suffix):
            save_to_database(vanity_address, secret)
            print("Save wallet")
            print(vanity_address)

def save_to_database(public_key, secret_key):
    postgres_url = os.getenv("POSTGRES_URL")
    endpoint_id = "ep-falling-paper-a4a6awfy"  # reemplaza esto con tu endpoint ID real
    postgres_url += f"&options=endpoint%3D{endpoint_id}"
    
    conn = psycopg2.connect(postgres_url)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO vanity_addresses (public_key, secret_key) VALUES (%s, %s)",
        (public_key, secret_key)
    )
    conn.commit()
    cur.close()
    conn.close()

@app.route('/start', methods=['GET'])
def start_generation():
    suffix = request.args.get('suffix', 'pump')
    stop_event.clear()
    threading.Thread(target=generate_vanity_address, args=(suffix,)).start()
    return jsonify({"status": "started", "suffix": suffix})

@app.route('/stop', methods=['GET'])
def stop_generation():
    stop_event.set()
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)