import subprocess
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
chaincode_name = "basic1"

# クエリするキー
query_key = "asset1"

# 実行回数
num_iterations = 3

def run_command(command):
    """コマンドを実行し、標準出力を返す。エラーが発生した場合は例外を投げる。"""
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"コマンド実行エラー: {e.output}")
        return None

for i in range(num_iterations):
    print(f"===================== Invoke {i} value ===================================")
    print("=======================================================================")
    print(f"++Begin '{i}'")
    start_time = datetime.now(timezone.utc).isoformat()
    print(start_time)
    
    # チェーンコードのクエリ
    for org, config in organizations.items():
        # チェーンコードクエリコマンドの構築
        query_cmd = (
            f"docker exec cli peer chaincode query "
            f"-C {channel_name} "
            f"-n {chaincode_name} "
            f"-c '{{\"Args\":[\"ReadAsset\",\"{query_key}\"]}}' "  # 'query' を 'ReadAsset' に変更
            f"--peerAddresses {config['peer_address']} "
            f"--tls --tlsRootCertFiles {config['tls_cert_path']}"  # '--cafile' を '--tlsRootCertFiles' に変更
        )
        query_result = run_command(query_cmd)
        print(f"+++Value '{query_key}' in {org}:")
        print(query_result if query_result else "クエリ失敗")
    
    # ブロックチェーン情報の取得
    for org, config in organizations.items():
        # チャネル情報取得コマンドの構築
        getinfo_cmd = (
            f"docker exec cli peer channel getinfo "
            f"-c {channel_name} "
            f"--tls --certfile {config['tls_cert_path']}"
            f"env CORE_PEER_ADDRESS={config['peer_address']}"
        )
        getinfo_result = run_command(getinfo_cmd)
        print(f"+++Info of blockchain in {org}:")
        print(getinfo_result if getinfo_result else "情報取得失敗")
    
    end_time = datetime.now(timezone.utc).isoformat()
    print(f"++Finish '{i}'")
    print("ELAPSED TIME in ms:")
    # 経過時間の計測
    try:
        start_timestamp = datetime.fromisoformat(start_time)
        end_timestamp = datetime.fromisoformat(end_time)
        elapsed_time_ms = int((end_timestamp - start_timestamp).total_seconds() * 1000)
    except ValueError:
        elapsed_time_ms = "計測失敗"
    print(elapsed_time_ms)
    print(end_time)
    print("\n\n")
