import subprocess
import re
from datetime import datetime
import time  # スリープのためのモジュール

# 組織ごとの設定
organizations = {
    "org1": {
        "peer_address": "peer0.org1.example.com:7051",
        "tls_cert_path": "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt",
    },
    "org2": {
        "peer_address": "peer0.org2.example.com:9051",
        "tls_cert_path": "/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt",
    }
}

channel_name = "mychannel"
chaincode_name = "basic2"  # チェーンコード名を変数として管理

def run_command(command):
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command execution error: {e.output}")
        return None

def send_transaction_batch():
    """バッチトランザクションを送信する"""
    command = (
        "docker exec cli peer chaincode invoke -o orderer.example.com:7050 "
        f"-C {channel_name} -n {chaincode_name} -c '{{\"function\":\"CreateAssetsBatch\",\"Args\":[\"50\"]}}' "
        "--tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/tls/ca.crt"
    )
    print("Submitting transaction batch...")
    run_command(command)
    print("Transaction batch submitted")

def get_latest_block_info(org, config):
    """最新ブロックの情報を取得してデコードする"""
    command = (
        f"docker exec cli peer channel fetch newest /tmp/latest.block "
        f"-c {channel_name} --tls --ordererTLSHostnameOverride orderer.example.com --cafile {config['tls_cert_path']}"
    )
    result = run_command(command)
    if not result:
        print(f"Failed to fetch the latest block for {org}")
        return None

    inspect_command = f"docker exec cli configtxlator proto_decode --input /tmp/latest.block --type common.Block"
    result = run_command(inspect_command)
    if not result:
        print(f"Failed to decode the latest block for {org}")
        return None

    return result

def get_block_timestamp(result):
    """結果からタイムスタンプを抽出する"""
    timestamp_line = [line for line in result.split('\n') if 'timestamp' in line]
    if timestamp_line:
        timestamp = re.search(r'"timestamp":\s+"(.*?)"', timestamp_line[0])
        return timestamp.group(1) if timestamp else "Timestamp not found"
    return "Timestamp not found"

def main():
    send_transaction_batch()  # トランザクションを送信

    block_timestamps = {org: None for org in organizations}  # 初期化
    initial_check = True
    while True:
        all_timestamps_obtained = True  # ブロックタイムスタンプが全て取得できたか確認
            
        for org, config in organizations.items():
            print(f"Fetching block information for {org}...")
            result = get_latest_block_info(org, config)
            if result:
                timestamp = get_block_timestamp(result)
                if initial_check:
                    initial_check = False
                    block_timestamps[org] = timestamp
                elif block_timestamps[org] != timestamp:
                    block_timestamps[org] = timestamp
                    print(f"{org} new block timestamp: {timestamp}")
            else:
                all_timestamps_obtained = False  # 取得できない場合フラグをスイッチ
            
        if all_timestamps_obtained:
            break  # 全てのタイムスタンプが取得できたらループを終了
        
        time.sleep(5)  # 一定時間待ちながら再チェック

    org_keys = list(organizations.keys())
    print("\n=== Block Timestamp Offsets ===")
    for i in range(len(org_keys)):
        for j in range(i + 1, len(org_keys)):
            org1, org2 = org_keys[i], org_keys[j]
            if block_timestamps[org1] and block_timestamps[org2]:
                t1 = datetime.fromisoformat(block_timestamps[org1].replace('Z', '+00:00'))
                t2 = datetime.fromisoformat(block_timestamps[org2].replace('Z', '+00:00'))
                offset = abs((t2 - t1).total_seconds() * 1000)  # ミリ秒単位
                print(f"Offset between {org1} and {org2}: {offset:.2f} ms")
            else:
                print(f"Could not compare {org1} and {org2} due to missing values.")

if __name__ == "__main__":
    main()
