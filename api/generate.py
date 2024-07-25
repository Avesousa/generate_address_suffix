import json
import os
import threading
import logging
import psycopg2
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from base58 import b58encode
from flask import Flask, request, jsonify
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.info(f"Wallet generated: ${vanity_address}")
            save_to_database(vanity_address, secret)

def save_to_database(public_key, secret_key):
    try:
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
        logger.info(f"Saved address {public_key} to database")
    except Exception as e:
        logger.error(f"Error saving to database {e}")

@app.route('/start', methods=['GET'])
def start_generation():
    suffix = request.args.get('suffix', 'pump')
    stop_event.clear()
    threading.Thread(target=generate_vanity_address, args=(suffix,)).start()
    logger.info(f"Started generation process with {suffix} like suffix")
    return jsonify({"status": "started", "suffix": suffix})

@app.route('/stop', methods=['GET'])
def stop_generation():
    stop_event.set()
    logger.info("Stopped generation process")
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    app.run(debug=True)