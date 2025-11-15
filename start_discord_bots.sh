#!/bin/bash

# --- ログ用ディレクトリの準備 ---
mkdir -p /home/jikkou/attendance_bot/logs
mkdir -p /home/jikkou/pdf_bot/logs
# ★追加
mkdir -p /home/jikkou/presence_app/logs

# --- attendance_bot の起動 ---
echo "Starting Attendance Bot..."
cd /home/jikkou/attendance_bot/
# 例: source /home/jikkou/attendance_bot/venv/bin/activate
/usr/bin/python3 /home/jikkou/attendance_bot/discord_bot.py > /home/jikkou/attendance_bot/logs/bot.log 2>&1 &
ATTENDANCE_BOT_PID=$!
echo "Attendance Bot started with PID $ATTENDANCE_BOT_PID"

# --- pdf_bot の起動 ---
echo "Starting PDF Bot..."
cd /home/jikkou/pdf_bot/
# 例: source /home/jikkou/pdf_bot/venv/bin/activate
/usr/bin/python3 /home/jikkou/pdf_bot/pdf_bot3.py > /home/jikkou/pdf_bot/logs/bot.log 2>&1 &
PDF_BOT_PID=$!
echo "PDF Bot started with PID $PDF_BOT_PID"


# presence_app(在室管理) の起動 ---
echo "Starting Presence App..."
# ★前提: アプリのパスが /home/jikkou/presence_app/ であること
cd /home/jikkou/presence_app/

# 仮想環境 (venv) を有効化 (パスが違う場合は修正してください)
echo "Activating presence_app venv..."
source /home/jikkou/presence_app/venv/bin/activate

# 1. app.py (Webサーバー) を起動
echo "Starting app.py..."
python3 /home/jikkou/presence_app/app.py > /home/jikkou/presence_app/logs/app.log 2>&1 &
PRESENCE_APP_PID=$!
echo "app.py started with PID $PRESENCE_APP_PID"

# 2. scanner.py (スキャナー) を起動
echo "Starting scanner.py..."
python3 /home/jikkou/presence_app/scanner.py > /home/jikkou/presence_app/logs/scanner.log 2>&1 &
PRESENCE_SCANNER_PID=$!
echo "scanner.py started with PID $PRESENCE_SCANNER_PID"

# --- ★★★ ここまで追加 ★★★ ---


# ★修正: 4つのプロセスすべてを待つ
echo "Shell script will now wait for all 4 processes..."
wait $ATTENDANCE_BOT_PID $PDF_BOT_PID $PRESENCE_APP_PID $PRESENCE_SCANNER_PID

echo "One or more processes have terminated. Shell script exiting."