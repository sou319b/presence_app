import json
import os
from flask import Flask, request, jsonify, send_from_directory, Response

# Flaskアプリの初期化
app = Flask(__name__)

# ★パスワードは "jikkou" に設定されています
ADMIN_PASSWORD = "jikkou"

# このファイルがあるディレクトリのパス
APP_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(APP_DIR, 'users.json')
STATUS_FILE = os.path.join(APP_DIR, 'status.json')

# --- データベース（JSONファイル）の読み書き ---

def read_users():
    """users.jsonを読み込む"""
    if not os.path.exists(USERS_FILE):
        return [] # ファイルがなければ空のリスト
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_users(users):
    """users.jsonに書き込む"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# --- APIエンドポイントの定義 ---

@app.route('/')
def index():
    """トップページ (index.html) を表示する"""
    return send_from_directory(APP_DIR, 'index.html')

@app.route('/index.html')
def index_page():
    """/index.html でもトップページを表示する"""
    return send_from_directory(APP_DIR, 'index.html')

# ★★★ 修正点：以下の2つの関数（ルート）を追加 ★★★

@app.route('/login.html')
def login_page():
    """login.html を表示する"""
    return send_from_directory(APP_DIR, 'login.html')

@app.route('/admin.html')
def admin_page():
    """admin.html を表示する"""
    return send_from_directory(APP_DIR, 'admin.html')

# ★★★ ここまで ★★★


@app.route('/api/data')
def get_data():
    """UIが必要とする全データを返す (ユーザーリスト + 在室状況)"""
    users = read_users()
    
    # status.json がまだ存在しない場合
    if not os.path.exists(STATUS_FILE):
        status_data = {}
    else:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
            
    return jsonify({
        'users': users,
        'status': status_data
    })

@app.route('/api/add_user', methods=['POST'])
def add_user():
    """Web UIから新しいユーザーを追加する"""
    data = request.json

    if not data or data.get('password') != ADMIN_PASSWORD:
        return jsonify({'success': False, 'message': 'パスワードが正しくありません'}), 401

    if not data or 'name' not in data or 'mac' not in data or 'category' not in data:
        return jsonify({'success': False, 'message': '必要な情報が不足しています'}), 400
        
    users = read_users()
    
    # MACアドレスが重複していないかチェック
    if any(u['mac'].lower() == data['mac'].lower() for u in users):
        return jsonify({'success': False, 'message': 'このMACアドレスは既に使用されています'}), 400

    new_user = {
        'name': data['name'],
        'mac': data['mac'].upper(), # MACアドレスは大文字に統一
        'category': data['category']
    }
    users.append(new_user)
    write_users(users)
    
    return jsonify({'success': True, 'user': new_user})

@app.route('/api/delete_user', methods=['POST'])
def delete_user():
    """ユーザーを削除する"""
    data = request.json

    if not data or data.get('password') != ADMIN_PASSWORD:
        return jsonify({'success': False, 'message': 'パスワードが正しくありません'}), 401
        
    if not data or 'mac' not in data:
        return jsonify({'success': False, 'message': 'MACアドレスが指定されていません'}), 400

    mac_to_delete = data['mac'].upper()
    users = read_users()
    
    # 削除対象を除いた新しいリストを作成
    new_users = [user for user in users if user['mac'] != mac_to_delete]
    
    if len(users) == len(new_users):
        return jsonify({'success': False, 'message': '該当するユーザーが見つかりません'}), 404
        
    write_users(new_users)
    return jsonify({'success': True})

# --- Flaskサーバーの起動 ---
if __name__ == '__main__':
    # 外部からのアクセスを許可するために host='0.0.0.0' を指定
    # ポートは 5000 番を使用 (8000番でも可)
    app.run(host='0.0.0.0', port=5000, debug=False)