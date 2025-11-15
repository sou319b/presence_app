#!/bin/bash

TARGET_MAC="54:10:4F:4F:F1:62"
SCAN_DURATION=8

# このスクリプトが置かれているフォルダ ( ~/presence_app )
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# JSONファイルの出力先
STATUS_FILE="$APP_DIR/status.json"

echo "[$TARGET_MAC] を $SCAN_DURATION 秒間スキャンします..."
result=$(timeout $SCAN_DURATION bluetoothctl scan on 2>&1)

# 現在時刻を取得
current_time=$(date '+%Y-%m-%d %H:%M:%S')

if echo "$result" | grep -q "$TARGET_MAC"; then
    echo "結果: 在室しています"
    # "在室" 情報をJSONファイルに出力
    echo "{\"status\": \"在室\", \"last_update\": \"$current_time\"}" > "$STATUS_FILE"
else
    echo "結果: 不在です"
    # "不在" 情報をJSONファイルに出力
    echo "{\"status\": \"不在\", \"last_update\": \"$current_time\"}" > "$STATUS_FILE"
fi

