import subprocess
import sys

def run_command(command):
    """シェルコマンドを実行し、結果を返す"""
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"コマンド実行エラー: {e.output}")
        return None

def fetch_and_get_block_size(block_number, channel_name, output_dir):
    """ブロックを取得し、そのサイズを返す"""
    block_filename = f"block{block_number}.block"
    block_path = f"{output_dir}/{block_filename}"

    # ブロックを取得するコマンド
    fetch_command = (
        f"docker exec cli peer channel fetch {block_number} {block_filename} "
        f"-c {channel_name} "
        "--tls "
        "--ordererTLSHostnameOverride orderer.example.com "
        "--cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/"
        "example.com/orderers/orderer.example.com/tls/ca.crt"
    )

    # コマンドの実行
    result = run_command(fetch_command)
    if result is None:
        print(f"ブロック{block_number}の取得に失敗しました。")
        return None

    # ブロックサイズを取得するコマンド
    size_command = f"docker exec cli stat -c %s {block_filename}"
    size_result = run_command(size_command)
    if size_result is None:
        print(f"ブロック{block_number}のサイズ取得に失敗しました。")
        return None

    # サイズをバイト単位で返す
    return int(size_result)

def main():
    # チャネル名とブロック番号範囲の指定
    channel_name = "mychannel"  # 必要に応じて変更
    start_block = int(input("開始ブロック番号を入力してください: "))
    end_block = int(input("終了ブロック番号を入力してください: "))

    # 出力ディレクトリ（CLIコンテナ内）
    output_dir = "/opt/gopath/src/github.com/hyperledger/fabric/peer"

    # 各ブロックのサイズを取得して表示
    block_sizes = {}
    for block_number in range(start_block, end_block + 1):
        print(f"ブロック{block_number}を取得しています...")
        block_size = fetch_and_get_block_size(block_number, channel_name, output_dir)
        if block_size is not None:
            block_sizes[block_number] = block_size
            print(f"ブロック{block_number}のサイズ: {block_size} バイト")
        else:
            print(f"ブロック{block_number}のサイズ取得に失敗しました。")
        print("-" * 50)

    # 統計情報の表示
    if block_sizes:
        total_blocks = len(block_sizes)
        total_size = sum(block_sizes.values())
        average_size = total_size / total_blocks
        max_size_block = max(block_sizes, key=block_sizes.get)
        min_size_block = min(block_sizes, key=block_sizes.get)

        print("\n=== 統計情報 ===")
        print(f"総ブロック数: {total_blocks}")
        print(f"合計サイズ: {total_size} バイト")
        print(f"平均サイズ: {average_size:.2f} バイト")
        print(f"最大サイズ: {block_sizes[max_size_block]} バイト (ブロック{max_size_block})")
        print(f"最小サイズ: {block_sizes[min_size_block]} バイト (ブロック{min_size_block})")

if __name__ == "__main__":
    main()
