import subprocess
import re
from datetime import datetime, timezone

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

# チャネル名とチェーンコード名
channel_name = "mychannel"

# 実験再現のためのツールコマンド
def set_network_delay(delay_ms):
    """TCコマンドを使用してネットワーク遅延を設定する"""
    command = f"sudo tc qdisc add dev ens33 root netem delay {delay_ms}ms"
    result = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Warning: {result.stderr.decode().strip()}")
        print("Skipping delay setup due to error.")
    else:
        print(f"Network delay set to {delay_ms}ms")

def clear_network_delay():
    """TCネットワーク遅延の解除"""
    command = "sudo tc qdisc del dev ens33 root netem"
    subprocess.run(command, shell=True, stderr=subprocess.DEVNULL)
    print("Network delay cleared")

def run_command(command):
    """コマンドを実行し、標準出力を返す。
    エラーが発生した場合はNoneを返す。
    """
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command execution error: {e.output}")
        return None

# ブロックのタイムスタンプの取得
def get_block_timestamp(org, config, block_number):
    # ブロックを取得
    command = (
        f"docker exec cli peer channel fetch newest /tmp/block{block_number}.block "
        f"-c {channel_name} --tls --certfile {config['tls_cert_path']}"
    )
    result = run_command(command)
    if not result:
        print(f"Failed to fetch block {block_number} for {org}")
        return None

    # ブロックの情報をデコード
    inspect_command = f"docker exec cli configtxlator proto_decode --input /tmp/block{block_number}.block --type common.Block"
    result = run_command(inspect_command)
    if not result:
        print(f"Failed to decode block {block_number} for {org}")
        return None

    # タイムスタンプの抽出
    timestamp_line = [line for line in result.split('\n') if 'timestamp' in line]
    if timestamp_line:
        # ISOフォーマットの日時として取得
        timestamp = re.search(r'"timestamp":\s+"(.*?)"', timestamp_line[0])
        return timestamp.group(1) if timestamp else "Timestamp not found"
    return "Timestamp not found"

# 主処理
def main():
    block_number = 10  # サンプル取得するブロック番号
    delay_ms = [0, 1000, 2000, 3000, 90000]  # ネットワーク遅延の値

    for delay in delay_ms:
        print(f"\n===== Testing with {delay}ms network delay =====")
        set_network_delay(delay)

        # 各組織からタイムスタンプを取得
        timestamps = {}
        for org, config in organizations.items():
            print(f"Fetching block timestamp for {org}")
            timestamps[org] = get_block_timestamp(org, config, block_number)
            if timestamps[org]:
                print(f"{org}: {timestamps[org]}")
            else:
                print(f"{org}: Failed to retrieve timestamp")

        # オフセットの計算
        print("\n=== Timestamp Offsets ===")
        org_keys = list(organizations.keys())
        for i in range(len(org_keys)):
            for j in range(i + 1, len(org_keys)):
                org1, org2 = org_keys[i], org_keys[j]
                if timestamps[org1] and timestamps[org2]:
                    t1 = datetime.fromisoformat(timestamps[org1].replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(timestamps[org2].replace('Z', '+00:00'))
                    offset = abs((t2 - t1).total_seconds() * 1000)  # ミリ秒単位で計算
                    print(f"Offset between {org1} and {org2}: {offset:.2f} ms")
        clear_network_delay()

if __name__ == "__main__":
    main()

