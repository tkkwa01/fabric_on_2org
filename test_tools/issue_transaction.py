import subprocess
import re
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
chaincode_name = "basic2"

def run_command(command):
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command execution error: {e.output}")
        return None

def send_transaction(tx_id):
    """単一のトランザクションを送信する"""
    asset_id = f"test{tx_id}"
    command = (
        "docker exec cli peer chaincode invoke -o orderer.example.com:7050 "
        f"-C {channel_name} -n {chaincode_name} "
        f'-c \'{{"function":"CreateAsset","Args":["{asset_id}", "color{tx_id}", "{tx_id}", "owner{tx_id}", "{tx_id}00"]}}\' '
        "--tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt"
    )
    print(f"Submitting transaction {tx_id}...")
    result = run_command(command)
    if result:
        print(f"Transaction {tx_id} submitted successfully.")
    else:
        print(f"Failed to submit transaction {tx_id}.")

def main():
    transaction_count = 30  # 発行するトランザクションの総数
    tx_id = 0

    while tx_id < transaction_count:
        start_time = time.time()
        tx_id += 1
        send_transaction(tx_id)
        elapsed_time = time.time() - start_time
        sleep_time = max(0, 0.085 - elapsed_time)
        time.sleep(sleep_time)

    print("All transactions have been submitted.")

if __name__ == "__main__":
    main()


