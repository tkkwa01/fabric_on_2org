import os
import glob

# 現在のディレクトリから対象のtxtファイルを取得
file_pattern = "*.txt"
files = glob.glob(file_pattern)

# 全てのデータを保持するリスト
all_data = []

# ファイルごとにデータを読み取る
for file in files:
    with open(file, "r") as f:
        lines = f.readlines()
        data = []
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("+") or line.startswith("0"):
                try:
                    data.append(float(line))
                except ValueError:
                    continue
        all_data.append(data)

# 各行の平均を計算
if all_data:
    max_lines = max(len(data) for data in all_data)
    averages = []
    for i in range(max_lines):
        values = [data[i] for data in all_data if i < len(data)]
        avg = sum(values) / len(values)
        averages.append(avg)

    # 平均値を出力
    output_file = "average.txt"
    with open(output_file, "w") as f:
        for avg in averages:
            sign = "+" if avg >= 0 else ""
            f.write(f"{sign}{avg:.5f}\n")

    print(f"平均値を {output_file} に出力しました。")
else:
    print("データが見つかりませんでした。")


