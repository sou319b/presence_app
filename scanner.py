import json
import os
import subprocess
import time
from datetime import datetime

# このファイルがあるディレクトリのパス
APP_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(APP_DIR, 'users.json')
STATUS_FILE = os.path.join(APP_DIR, 'status.json')

# ★「不在」と判定するまでの猶予時間 (デバッグ用に 1分)
TIMEOUT_MINUTES = 1

def read_users():
    """users.jsonを読み込む"""
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("users.json の読み込みに失敗しました。")
        return []

def read_status():
    """status.jsonを読み込む"""
    if not os.path.exists(STATUS_FILE):
        return {}
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("status.json の読み込みに失敗しました。")
        return {}

def write_status(status_data):
    """status.jsonに書き込む"""
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)

# ★★★ ここからが変更点 ★★★
def check_device_presence(mac):
    """l2ping を使ってデバイスの存在確認を行う"""
    print(f"Checking presence of {mac}...")
    try:
        # l2ping コマンドを実行
        # -c 1: 1回だけpingを送る
        # -t 1: タイムアウトを1秒にする (応答が遅い場合は 2 や 3 に増やす)
        result = subprocess.run(
            ['l2ping', '-c', '1', '-t', '1', mac],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            timeout=3 # l2ping自体が固まった場合の保険タイムアウト
        )
        
        # 成功時 (stdout に "bytes from" が含まれる)
        if result.returncode == 0 and "bytes from" in result.stdout:
            # print(f"Found: {mac}")
            return True
        else:
            # 失敗時 (タイムアウトなど)
            # print(f"Not found: {mac} (Return: {result.returncode})")
            return False
            
    except FileNotFoundError:
        print(f"エラー: 'l2ping' コマンドが見つかりません。")
        print("sudo apt install bluez-utils を試してください。")
        # l2ping がない場合、どうしようもないので False を返し続ける
        return False
    except subprocess.TimeoutExpired:
        print(f"l2pingがタイムアウトしました ({mac})")
        return False
    except Exception as e:
        print(f"l2ping実行中にエラーが発生しました ({mac}): {e}")
        return False
# ★★★ ここまでが変更点 ★★★

def main():
    users = read_users()
    if not users:
        print("対象ユーザーが登録されていません。users.jsonを確認してください。")
        return

    target_macs = {user['mac']: user['name'] for user in users}
    
    current_time_iso = datetime.now().isoformat()
    current_time_epoch = time.time()
    
    # 既存のステータスを読み込む
    status_data = read_status()

    # ★★★ ここからが変更点 ★★★
    # 登録されている全MACアドレスに対して個別に存在確認
    found_macs = set()
    print("--- 存在確認ループ開始 ---")
    for mac, name in target_macs.items():
        if check_device_presence(mac):
            found_macs.add(mac)
            print(f"  -> 発見: {name} ({mac})")
        # 1台ずつチェックすると時間がかかるため、少し待機
        time.sleep(0.2) # 0.2秒待機
    print("--- 存在確認ループ終了 ---")
    # ★★★ ここまでが変更点 ★★★


    # ステータスを更新 (このロジックは元のファイルと同じ)
    for mac in target_macs:
        if mac in found_macs:
            # 見つかった場合：ステータスを「在室」にし、最終確認時刻を更新
            status_data[mac] = {
                'status': '在室',
                'last_seen': current_time_iso
            }
        else:
            # 見つからなかった場合
            if mac in status_data and status_data[mac].get('last_seen') != 'N/A':
                # タイムアウト処理
                last_seen_epoch = datetime.fromisoformat(status_data[mac]['last_seen']).timestamp()
                if (current_time_epoch - last_seen_epoch) > (TIMEOUT_MINUTES * 60):
                    # 1分以上見つからなければ「不在」にする
                    status_data[mac]['status'] = '不在'
                else:
                    # 1分以内なら、まだ「在室」扱い
                    pass 
            else:
                # 履歴がないか、'N/A' だった場合
                if mac not in status_data:
                    status_data[mac] = {
                        'status': '不在',
                        'last_seen': 'N/A'
                    }
                elif status_data[mac].get('status') != '不在':
                     status_data[mac]['status'] = '不在'


    # 更新したステータスをファイルに書き込む
    write_status(status_data)
    print("status.json を更新しました。")

if __name__ == "__main__":
    # 無限ループで定期的に実行
    while True:
        main()
        # ★待機時間 (デバッグ用に 10秒)
        # (ユーザー数 * (l2pingのタイムアウト秒数+0.2秒) よりも長くする必要がある)
        print("10秒待機します...")
        time.sleep(10)
        