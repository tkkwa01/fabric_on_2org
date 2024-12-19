import os
import re
from datetime import datetime

# 日時フォーマットを設定
datetime_format = "%Y-%m-%d %H:%M:%S.%f UTC"

# ブロックの受信時間を取得する関数
def extract_block_times(log_file, pattern):
    block_times = {}
    with open(log_file, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                timestamp = datetime.strptime(match.group(1), datetime_format)
                block_number = int(match.group(2))
                block_times[block_number] = timestamp
    return block_times

# 入力ディレクトリの確認とファイルパス取得
def get_log_file_paths():
    while True:
        log_dir = input("ログファイルが格納されたディレクトリを入力してください: ").strip()
        if not os.path.isdir(log_dir):
            print("エラー: 指定されたディレクトリが存在しません。再度入力してください。")
            continue
        org1_log = os.path.join(log_dir, "org1_peer_log.txt")
        org2_log = os.path.join(log_dir, "org2_peer_log.txt")
        orderer_log = os.path.join(log_dir, "orderer_log.txt")
        if not (os.path.isfile(org1_log) and os.path.isfile(org2_log) and os.path.isfile(orderer_log)):
            print("エラー: 必要なログファイルがディレクトリ内に存在しません。再度入力してください。")
            continue
        return org1_log, org2_log, orderer_log

# 出力ディレクトリの確認
def get_output_directory():
    while True:
        output_dir = input("結果を保存する出力先ディレクトリを入力してください: ").strip()
        if not os.path.isdir(output_dir):
            print("エラー: 指定されたディレクトリが存在しません。再度入力してください。")
            continue
        return output_dir

# 出力ファイル名を決定する関数
def get_output_filename(output_dir, base_name="offset.txt"):
    # 指定したディレクトリ内で "offset.txt", "offset2.txt", "offset3.txt", ... を探す
    base_path = os.path.join(output_dir, base_name)
    if not os.path.exists(base_path):
        return base_path
    counter = 2
    while True:
        new_name = os.path.join(output_dir, f"offset{counter}.txt")
        if not os.path.exists(new_name):
            return new_name
        counter += 1

# ログパターン
peer_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} UTC).*?Received block \[(\d+)\]"
orderer_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} UTC).*?Writing block \[(\d+)\]"

# メイン処理
if __name__ == "__main__":
    # 入力ログディレクトリを取得
    org1_log, org2_log, orderer_log = get_log_file_paths()

    # 出力先ディレクトリを取得
    output_dir = get_output_directory()

    # データを取得
    org1_times = extract_block_times(org1_log, peer_pattern)
    org2_times = extract_block_times(org2_log, peer_pattern)
    orderer_times = extract_block_times(orderer_log, orderer_pattern)

    # 結果を格納するリスト
    offset_diffs = []

    # 時間差を計算して出力
    print("Block Number | Orderer Time         | Org1 Time            | Org2 Time            | Org1 Offset (s) | Org2 Offset (s) | Offset Diff (s)")
    print("-" * 140)
    for block in sorted(set(orderer_times.keys()) & set(org1_times.keys()) & set(org2_times.keys())):
        orderer_time = orderer_times[block]
        org1_time = org1_times[block]
        org2_time = org2_times[block]
        org1_offset = (org1_time - orderer_time).total_seconds()
        org2_offset = (org2_time - orderer_time).total_seconds()
        offset_diff = org2_offset - org1_offset
        offset_diffs.append(offset_diff)
        diff_sign = "+" if offset_diff >= 0 else "-"
        print(f"{block:12} | {orderer_time} | {org1_time} | {org2_time} | {org1_offset:.3f}         | {org2_offset:.3f}         | {diff_sign}{abs(offset_diff):.3f}")

    # Offset Diff (s)列のみを出力ディレクトリにファイル出力
    output_file = get_output_filename(output_dir)
    with open(output_file, "w") as f:
        for diff in offset_diffs:
            diff_sign = "+" if diff >= 0 else "-"
            f.write(f"{diff_sign}{abs(diff):.3f}\n")
        f.write("-" * 16 + "\n")
        total_diff = sum(offset_diffs)
        avg_diff = total_diff / len(offset_diffs)
        f.write(f"Total:{total_diff:+.5f}\n")
        f.write(f"Average:{avg_diff:+.5f}\n")

    print(f"\nOffset Diff (s)の結果が '{output_file}' に出力されました。")

