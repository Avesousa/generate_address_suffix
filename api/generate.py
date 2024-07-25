import json
import os
import threading
import psycopg2
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from base58 import b58encode
from flask import Flask, request, jsonify

app = Flask(__name__)
stop_event = threading.Event()

app = Flask(__name__)
stop_event = threading.Event()

def generate_vanity_address(suffix: str):
    while not stop_event.is_set():
        keypair = Keypair()
        vanity_address = b58encode(str(keypair.pubkey())).decode('utf-8')
        secret = b58encode(keypair.secret()).decode('utf-8')
        print(vanity_address)
        if vanity_address.endswith(suffix):
            save_to_database(vanity_address, keypair.pubkey(), secret)
            print("Save wallet")
            print(vanity_address)

def save_to_database(vanity_address, public_key, secret_key):
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO vanity_addresses (vanity_address, public_key, secret_key) VALUES (%s, %s, %s)",
        (vanity_address, public_key.to_base58().decode('utf-8'), b58encode(secret_key).decode('utf-8'))
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
    app.run(debug=True)