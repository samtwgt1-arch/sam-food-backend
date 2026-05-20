"""
Flask Backend for ChromaDB Admin Panel
包裝 ChromaDB + 管理 API + 靜態管理介面
"""

import os
import hashlib
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, render_template_string
import chromadb
from chromadb.config import Settings

# ============== 初始化 ==============
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')  # 生產環境請更換

# ============== ChromaDB 客戶端 ==============
CHROMA_DATA_PATH = os.environ.get('CHROMA_DATA_PATH', './chromadb_data')

def get_chroma_client():
    """取得 ChromaDB 客戶端"""
    return chromadb.PersistentClient(path=CHROMA_DATA_PATH)

def get_collection(name='taipei_food'):
    """取得指定 Collection"""
    client = get_chroma_client()
    try:
        return client.get_collection(name)
    except:
        return client.create_collection(name)

# ============== 認證裝飾器 ==============
def require_auth(f):
    """簡單的密碼保護裝飾器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('X-Auth-Password', '')
        if auth != app.config['ADMIN_PASSWORD']:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# ============== API 路由 ==============

@app.route('/api/health')
def health():
    """健康檢查"""
    return jsonify({'status': 'ok', 'chroma_path': CHROMA_DATA_PATH})

@app.route('/api/collections')
@require_auth
def list_collections():
    """列出所有 Collections"""
    client = get_chroma_client()
    collections = client.list_collections()
    return jsonify({
        'collections': [
            {
                'name': c.name,
                'count': c.count(),
                'metadata': c.metadata
            } for c in collections
        ]
    })

@app.route('/api/collections/<name>')
@require_auth
def get_collection_info(name):
    """取得 Collection 詳細資訊"""
    client = get_chroma_client()
    try:
        col = client.get_collection(name)
        return jsonify({
            'name': col.name,
            'count': col.count(),
            'metadata': col.metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/collections/<name>/items')
@require_auth
def get_collection_items(name):
    """取得 Collection 所有項目（分頁）"""
    client = get_chroma_client()
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    try:
        col = client.get_collection(name)
        results = col.get(include=['documents', 'metadatas', 'embeddings'])
        
        items = []
        docs = results.get('documents', [])
        metas = results.get('metadatas', [])
        embs = results.get('embeddings', [])
        ids = results.get('ids', [])
        
        for i in range(min(len(docs), limit)):
            idx = offset + i
            if idx < len(docs):
                # 過濾 None 和 ndarray 类型的 embedding
                emb = None
                if i < len(embs) and embs[idx] is not None:
                    try:
                        emb_list = embs[idx]
                        if hasattr(emb_list, 'tolist'):
                            emb_list = emb_list.tolist()
                        # 只取前128維壓縮
                        if isinstance(emb_list, list) and len(emb_list) > 128:
                            emb_list = emb_list[:128]
                        emb = emb_list
                    except:
                        emb = None
                
                items.append({
                    'id': str(ids[idx]) if i < len(ids) else f'item_{idx}',
                    'document': str(docs[idx]) if docs[idx] is not None else '',
                    'metadata': metas[idx] if (i < len(metas) and metas[idx] is not None) else {},
                    'embedding': emb
                })
        
        return jsonify({
            'collection': name,
            'total': col.count(),
            'limit': limit,
            'offset': offset,
            'items': items
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections/<name>/query', methods=['POST'])
@require_auth
def query_collection(name):
    """語意搜尋"""
    client = get_chroma_client()
    data = request.json
    
    query_texts = data.get('query_texts', [''])
    n_results = int(data.get('n_results', 10))
    where_filter = data.get('where', None)
    
    try:
        col = client.get_collection(name)
        results = col.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where_filter,
            include=['documents', 'metadatas', 'distances']
        )
        
        # 格式化結果
        formatted = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                # 轉換 distance 避免 numpy 類型問題
                dist = None
                if results['distances'] and results['distances'][0] and i < len(results['distances'][0]):
                    try:
                        dist = float(results['distances'][0][i])
                    except:
                        dist = None
                
                formatted.append({
                    'id': str(results['ids'][0][i]),
                    'document': str(results['documents'][0][i]) if results['documents'] and results['documents'][0] else '',
                    'metadata': results['metadatas'][0][i] if (results['metadatas'] and results['metadatas'][0]) else {},
                    'distance': dist
                })
        
        return jsonify({
            'query': query_texts,
            'results': formatted
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections/<name>/add', methods=['POST'])
@require_auth
def add_items(name):
    """新增文件到 Collection"""
    client = get_chroma_client()
    data = request.json
    
    documents = data.get('documents', [])
    metadatas = data.get('metadatas', [])
    ids = data.get('ids', [f"item_{i}" for i in range(len(documents))])
    
    if not documents:
        return jsonify({'error': 'No documents provided'}), 400
    
    try:
        col = client.get_or_create_collection(name)
        col.add(
            documents=documents,
            metadatas=metadatas if metadatas else [{}] * len(documents),
            ids=ids
        )
        return jsonify({'success': True, 'added': len(documents)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections/<name>/delete', methods=['POST'])
@require_auth
def delete_items(name):
    """刪除文件"""
    client = get_chroma_client()
    data = request.json
    
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'error': 'No ids provided'}), 400
    
    try:
        col = client.get_collection(name)
        col.delete(ids=ids)
        return jsonify({'success': True, 'deleted': len(ids)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections', methods=['POST'])
@require_auth
def create_collection():
    """建立新 Collection"""
    client = get_chroma_client()
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({'error': 'Name required'}), 400
    
    try:
        col = client.create_collection(name=name)
        return jsonify({'success': True, 'name': col.name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collections/<name>', methods=['DELETE'])
@require_auth
def delete_collection(name):
    """刪除 Collection"""
    client = get_chroma_client()
    try:
        client.delete_collection(name)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== 管理介面 Static Files ==============

@app.route('/admin')
def admin_page():
    """管理介面主頁"""
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/admin/<path:filename>')
def admin_static(filename):
    """管理介面靜態資源"""
    return send_from_directory(app.static_folder, filename)

# ============== 登入頁面 ==============

LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登入 - 美食資料庫管理後台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        h1 { 
            color: #333; 
            margin-bottom: 30px;
            text-align: center;
            font-size: 24px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e1e1e1;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .error {
            color: #e74c3c;
            margin-top: 15px;
            text-align: center;
            display: none;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🔐 美食資料庫管理後台</h1>
        <div class="input-group">
            <label>管理密碼</label>
            <input type="password" id="password" placeholder="請輸入密碼" onkeypress="if(event.key==='Enter')login()">
        </div>
        <button class="btn" onclick="login()">登入</button>
        <p class="error" id="error">密碼錯誤</p>
    </div>

    <script>
        function login() {
            const password = document.getElementById('password').value;
            localStorage.setItem('admin_auth', password);
            // 驗證
            fetch('/api/health', {
                headers: { 'X-Auth-Password': password }
            }).then(r => {
                if (r.ok) {
                    window.location.href = '/admin';
                } else {
                    document.getElementById('error').style.display = 'block';
                    localStorage.removeItem('admin_auth');
                }
            }).catch(() => {
                document.getElementById('error').style.display = 'block';
            });
        }
    </script>
</body>
</html>
'''

@app.route('/login')
def login_page():
    return render_template_string(LOGIN_PAGE)

# ============== 啟動 ==============
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)