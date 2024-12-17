#!/bin/bash

channel_name="mychannel"
block_number=0

while true; do
    echo "Fetching block $block_number..."

    # 最新ブロックの取得とデコード
    docker exec cli peer channel fetch $block_number block_$block_number.block -c $channel_name
    docker exec cli configtxlator proto_decode --input block_$block_number.block --type common.Block --output block_$block_number.json

    # タイムスタンプの取得
    timestamp=$(docker exec cli jq -r '.data.data[0].payload.header.channel_header.timestamp' block_$block_number.json)

    # 出力
    echo "Block $block_number timestamp: $timestamp"

    # 次のブロックへ
    block_number=$((block_number + 1))

done

