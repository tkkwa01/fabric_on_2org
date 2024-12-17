import os
import re
from datetime import datetime

# 日時フォーマットを設定
datetime_format = "%Y-%m-%d %H:%M:%S.%f UTC"

# ブロックの受信時間を取得する関数
def extract_block_times(log_file, pattern, skip_first=False):
    block_times = {}
    with open(log_file, 'r') as file:
        first_line_skipped = False
        for line in file:
            if skip_first and not first_line_skipped:
                first_line_skipped = True
                continue
            match = re.search(pattern, line)
            if match:
                timestamp = datetime.strptime(match.group(1), datetime_format)
                block_number = int(match.group(2))
                block_times[block_number] = timestamp
    return block_times

# ディレクトリ入力とファイルパス取得
def get_log_file_paths():
    log_dir = input("ログファイルが格納されたディレクトリを入力してください: ").strip()
    org1_log = os.path.join(log_dir, "org1_peer_log.txt")
    org2_log = os.path.join(log_dir, "org2_peer_log.txt")
    orderer_log = os.path.join(log_dir, "orderer_log.txt")
    return org1_log, org2_log, orderer_log

# ログパターン
peer_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} UTC).*?Received block \[(\d+)\]"
orderer_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} UTC).*?Writing block \[(\d+)\]"

# メイン処理
if __name__ == "__main__":
    # ファイルパスを取得
    org1_log, org2_log, orderer_log = get_log_file_paths()

    # データを取得
    org1_times = extract_block_times(org1_log, peer_pattern)
    org2_times = extract_block_times(org2_log, peer_pattern)
    orderer_times = extract_block_times(orderer_log, orderer_pattern, skip_first=True)

    # 時間差を計算して出力
    print("Block Number | Orderer Time         | Org1 Time            | Org2 Time            | Org1 Offset (s) | Org2 Offset (s)")
    print("-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—-—")
    for block in sorted(set(orderer_times.keys()) & set(org1_times.keys()) & set(org2_times.keys())):
        orderer_time = orderer_times[block]
        org1_time = org1_times[block]
        org2_time = org2_times[block]
        org1_offset = (org1_time - orderer_time).total_seconds()
        org2_offset = (org2_time - orderer_time).total_seconds()
        print(f"{block:12} | {orderer_time} | {org1_time} | {org2_time} | {org1_offset:.3f}         | {org2_offset:.3f}")
