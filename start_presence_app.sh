#!/bin/bash

# このスクリプトがあるディレクトリ (/home/jikkou/presence_app) に移動
cd "$(dirname "$0")"

# app.py の起動
echo "Presence App (app.py) を起動します..."
/usr/bin/python3 /home/jikkou/presence_app/app.py > /home/jikkou/presence_app/app.log 2>&1 &
APP_PID=$!
echo "app.py がPID $APP_PID で起動しました"

# scanner.py の起動
echo "Presence Scanner (scanner.py) を起動します..."
/usr/bin/python3 /home/jikkou/presence_app/scanner.py > /home/jikkou/presence_app/scanner.log 2>&1 &
SCANNER_PID=$!
echo "scanner.py がPID $SCANNER_PID で起動しました"

echo "両方のスクリプトが終了するまで待機します..."
wait $APP_PID $SCANNER_PID

echo "1つ以上のスクリプトが終了しました。シェルスクリプトを終了します。"

