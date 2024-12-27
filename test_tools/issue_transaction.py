import subprocess
import re
import random
import string
from datetime import datetime
import time
import threading

# 組織ごとの設定
organizations = {
    "org1": {
        "peer_address": "peer0.org1.example.com:7051",
        "tls_cert_path": "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt",
        "msp_id": "Org1MSP",
        "msp_config_path": "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp",
    },
    "org2": {
        "peer_address": "peer0.org2.example.com:9051",
        "tls_cert_path": "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt",
        "msp_id": "Org2MSP",
        "msp_config_path": "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp",
    }
}

channel_name = "mychannel"
chaincode_name = "basic1"

def run_command(command):
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command execution error: {e.output}")
        return None

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def send_transaction(tx_id):
    """単一のトランザクションを送信する"""
    asset_id = f"test{tx_id}"
    color = f"color{tx_id}"
    size = tx_id
    owner = generate_random_string(4096)  # 長いランダムな所有者名
    appraised_value = tx_id * 100

    # Dockerコマンドを構築
    command = (
        "docker exec cli peer chaincode invoke -o orderer.example.com:7050 "
        f"-C {channel_name} -n {chaincode_name} "
        f'--peerAddresses {organizations["org1"]["peer_address"]} --tlsRootCertFiles {organizations["org1"]["tls_cert_path"]} '
        f'--peerAddresses {organizations["org2"]["peer_address"]} --tlsRootCertFiles {organizations["org2"]["tls_cert_path"]} '
        f'-c \'{{"Args":["CreateAsset", "{asset_id}", "{color}", "{size}", "{owner}", "{appraised_value}"]}}\' '
        "--tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt"
    )
    print(f"Submitting transaction {tx_id}...")
    result = run_command(command)
    if result:
        print(f"Transaction {tx_id} submitted successfully.")
    else:
        print(f"Failed to submit transaction {tx_id}.")

def main():
    transaction_count = 100  # 発行するトランザクションの総数
    start_tx_id = 900
    end_tx_id = start_tx_id + transaction_count

    tx_id = start_tx_id

    while tx_id < end_tx_id:
        start_time = time.time()
        send_transaction(tx_id)
        tx_id += 1
        elapsed_time = time.time() - start_time
        sleep_time = max(0, 0.085 - elapsed_time)
        time.sleep(sleep_time)

    print("All transactions have been submitted.")

if __name__ == "__main__":
    main()

