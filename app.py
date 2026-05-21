"""
Flask Backend for ChromaDB Admin Panel
包裝 ChromaDB + 管理 API + 靜態管理介面
"""

import os
import sys
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, render_template_string
import chromadb
from chromadb.config import Settings

# ============== 初始化 ==============
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin123')

# ============== ChromaDB 客戶端 ==============
CHROMA_DATA_PATH = os.environ.get('CHROMA_DATA_PATH', '/tmp/chromadb_data')

def get_chroma_client():
    """取得 ChromaDB 客戶端"""
    os.makedirs(CHROMA_DATA_PATH, exist_ok=True)
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

# ============== 台北吃到飽餐廳資料 ==============
TAIPEI_BUFFET_RESTAURANTS = [
    {
        "name": "饗饗",
        "category": "buffet",
        "rating": "4.8",
        "price_range": "1500-2500",
        "dinner_price": "2199",
        "lunch_price": "1799",
        "location": "台北市信義區",
        "features": ["高空景觀", "頂級海鮮", "日式料理", "義式料理"],
        "description": "微風信義47樓，提供高級吃到飽 buffet，景觀極佳，海鮮新鮮度高。"
    },
    {
        "name": "旭集",
        "category": "buffet",
        "rating": "4.7",
        "price_range": "1300-2000",
        "dinner_price": "1999",
        "lunch_price": "1599",
        "location": "台北市大安區",
        "features": ["日式料理", "龍蝦", "帝王蟹", "現做料理"],
        "description": "以日式料理為主的 buffet，提供新鮮龍蝦、帝王蟹等高級海鮮。"
    },
    {
        "name": "饗食天堂",
        "category": "buffet",
        "rating": "4.5",
        "price_range": "700-1500",
        "dinner_price": "1299",
        "lunch_price": "899",
        "location": "多家分店",
        "features": ["CP值高", "多樣化料理", "甜點區"],
        "description": "CP值極高的 buffet 選擇，料理種類多達百種，甜點區特別受歡迎。"
    },
    {
        "name": "寒舍艾美探索廚房",
        "category": "buffet",
        "rating": "4.6",
        "price_range": "1200-2000",
        "dinner_price": "1880",
        "lunch_price": "1480",
        "location": "台北市信義區",
        "features": ["五星飯店", "甜點區", "現做牛排", "高空景觀"],
        "description": "寒舍艾美酒店的自助餐廳，甜點區是最大亮點，提供多種精緻糕點。"
    },
    {
        "name": "君品酒店雲軒",
        "category": "buffet",
        "rating": "4.7",
        "price_range": "1500-2500",
        "dinner_price": "2180",
        "lunch_price": "1680",
        "location": "台北市大同區",
        "features": ["五星飯店", "現切牛排", "龍蝦", "港式料理"],
        "description": "君品酒店的吃到飽餐廳，現切牛排和龍蝦是招牌，港式料理也相當精緻。"
    },
    {
        "name": "台北晶華酒店 aze",
        "category": "buffet",
        "rating": "4.8",
        "price_range": "1800-2800",
        "dinner_price": "2580",
        "lunch_price": "1980",
        "location": "台北市中山區",
        "features": ["五星飯店", "帝王蟹", "龍蝦", "精緻甜點"],
        "description": "台北晶華酒店的自助餐廳，提供帝王蟹、龍蝦等頂級海鮮，甜點相當精緻。"
    },
    {
        "name": "Mega 50 望京樓",
        "category": "buffet",
        "rating": "4.5",
        "price_range": "800-1500",
        "dinner_price": "1399",
        "lunch_price": "999",
        "location": "新北市板橋區",
        "features": ["高空景觀", "CP值高", "粵式料理", "港式燒臘"],
        "description": "板橋高空景觀 buffet，CP值高，粵式料理和港式燒臘相當受歡迎。"
    },
    {
        "name": "漢來海港",
        "category": "buffet",
        "rating": "4.6",
        "price_range": "800-1500",
        "dinner_price": "1399",
        "lunch_price": "1099",
        "location": "多家分店",
        "features": ["CP值高", "海鮮多", "日式料理", "甜點"],
        "description": "以海鮮見長的吃到飽餐廳，蝦蟹貝類種類豐富，CP值極高。"
    },
    {
        "name": "豐FOOD",
        "category": "buffet",
        "rating": "4.4",
        "price_range": "700-1300",
        "dinner_price": "1199",
        "lunch_price": "799",
        "location": "台北市中山區",
        "features": ["CP值高", "多樣化", "日式料理", "鐵板燒"],
        "description": "CP值極高的 buffet，日式料理和鐵板燒都有一定水準，適合家庭聚餐。"
    },
    {
        "name": "青花苑",
        "category": "yakiniku",
        "rating": "4.6",
        "price_range": "1500-2500",
        "dinner_price": "2180",
        "lunch_price": "1680",
        "location": "台北市大安區",
        "features": ["頂級燒肉", "和牛", "伊比利豬", "包生菜"],
        "description": "頂級燒肉吃到飽，提供日本和牛、伊比利豬等高級肉品，需提前預訂。"
    },
    {
        "name": "燒肉天花板",
        "category": "yakiniku",
        "rating": "4.7",
        "price_range": "2000-3500",
        "dinner_price": "2980",
        "lunch_price": "2380",
        "location": "台北市松山區",
        "features": ["頂級燒肉", "和牛", "帝王蟹", "龍蝦"],
        "description": "頂級燒肉吃到飽，提供和牛、帝王蟹、龍蝦，適合慶祝特殊場合。"
    },
    {
        "name": "路易莎火烤兩吃",
        "category": "hotpot_yakiniku",
        "rating": "4.3",
        "price_range": "500-900",
        "dinner_price": "799",
        "lunch_price": "599",
        "location": "多家分店",
        "features": ["燒肉+火鍋", "CP值高", "多样化", "適合聚餐"],
        "description": "燒肉+火鍋複合店，CP值高，適合想吃燒肉又想吃火鍋的人。"
    }
]

@app.route('/api/reset', methods=['POST'])
@require_auth
def reset_db():
    """刪除並重建資料庫"""
    try:
        client = get_chroma_client()
        try:
            client.delete_collection('taipei_food')
        except:
            pass
        col = client.create_collection('taipei_food')
        col.add(
            ids=[f"r{i}" for i in range(12)],
            documents=[
                "探索廚房 - 評分 4.5 顆星，晚餐 NT$2,580，午餐 NT$1,980。位於台北信義區。特色：龍蝦、牛排、帝王蟹。",
                "三燔本家 - 評分 4.6 顆星，晚餐 NT$1,499，午餐 NT$1,299。位於台北中山區。特色：龍蝦、天使紅蝦、握壽司。",
                "台北君悅凱菲屋 - 評分 4.5 顆星，晚餐 NT$2,200，午餐 NT$1,800。位於台北信義區。特色：甜點區、各國料理。",
                "NAGOMI - 評分 4.7 顆星，晚餐 NT$1,690，午餐 NT$1,290。位於新北板橋區。特色：港式燒臘、生魚片。",
                "漢來海港 - 評分 4.4 顆星，晚餐 NT$1,380，午餐 NT$1,180。位於台北中山區。特色：CP值最高、分店多。",
                "星嶼沙拉吧 - 評分 4.5 顆星，晚餐 NT$888，午餐 NT$788。位於新北三重區。特色：素食友善、創意沙拉。",
                "涮乃葉 - 評分 4.3 顆星，晚餐 NT$768，午餐 NT$668。位於台北多家分店。特色：日式涮涮鍋、和牛。",
                "燒肉眾 - 評分 4.2 顆星，晚餐 NT$699，午餐 NT$599。位於台北公館/板橋。特色：日式燒肉、吃到飽。",
                "彩豐樓 - 評分 4.4 顆星，晚餐 NT$1,880，午餐 NT$1,580。位於台北中山區。特色：粵式料理、海鮮。",
                "旭集 - 評分 4.6 顆星，晚餐 NT$1,690，午餐 NT$1,290。位於台北信義區。特色：日式料理、甜點。",
                "十二廚 - 評分 4.3 顆星，晚餐 NT$2,000，午餐 NT$1,600。位於台北中山區。特色：各國料理、甜點。",
                "飪室 - 評分 4.5 顆星，晚餐 NT$699，午餐 NT$599。位於新北新莊區。特色：印度料理、素食友善。"
            ],
            metadatas=[
                {"name": "探索廚房", "rating": 4.5, "location": "台北信義區", "category": "頂級 Buffet"},
                {"name": "三燔本家", "rating": 4.6, "location": "台北中山區", "category": "日式 Buffet"},
                {"name": "台北君悅凱菲屋", "rating": 4.5, "location": "台北信義區", "category": "五星飯店"},
                {"name": "NAGOMI", "rating": 4.7, "location": "新北板橋區", "category": "日式 Buffet"},
                {"name": "漢來海港", "rating": 4.4, "location": "台北中山區", "category": "CP值最高"},
                {"name": "星嶼沙拉吧", "rating": 4.5, "location": "新北三重區", "category": "素食 Buffet"},
                {"name": "涮乃葉", "rating": 4.3, "location": "台北多家分店", "category": "日式火鍋"},
                {"name": "燒肉眾", "rating": 4.2, "location": "台北公館", "category": "日式燒肉"},
                {"name": "彩豐樓", "rating": 4.4, "location": "台北中山區", "category": "粵式 Buffet"},
                {"name": "旭集", "rating": 4.6, "location": "台北信義區", "category": "日式 Buffet"},
                {"name": "十二廚", "rating": 4.3, "location": "台北中山區", "category": "五星飯店"},
                {"name": "飪室", "rating": 4.5, "location": "新北新莊區", "category": "異國料理"}
            ]
        )
        return jsonify({'success': True, 'count': col.count()})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/init', methods=['POST'])
@require_auth
def init_data():
    """初始化台北吃到飽餐廳資料"""
    import sys
    print('START init_data', flush=True)
    try:
        client = get_chroma_client()
        print('Got client', flush=True)
        
        # 刪除舊 collection
        try:
            client.delete_collection('taipei_food')
            print('Deleted', flush=True)
        except Exception as e:
            print(f'Delete err: {e}', flush=True)
        
        # 建立或取得 collection
        try:
            col = client.create_collection('taipei_food')
            print('Created', flush=True)
        except Exception:
            col = client.get_collection('taipei_food')
            if col.count() > 0:
                all_data = col.get()
                if all_data and 'ids' in all_data:
                    col.delete(ids=all_data['ids'])
            print('Got existing', flush=True)
        
        # 只加入最基本的 12 筆記錄（每家餐廳 1 筆濃縮資訊）
        sample_restaurants = [
            {
                "id": "r0",
                "doc": "探索廚房 - 評分 4.5 顆星，晚餐 NT$2,580，午餐 NT$1,980。位於台北信義區。特色：龍蝦、牛排、帝王蟹。",
                "meta": {"name": "探索廚房", "rating": 4.5, "location": "台北信義區", "category": "頂級 Buffet"}
            },
            {
                "id": "r1",
                "doc": "三燔本家 - 評分 4.6 顆星，晚餐 NT$1,499，午餐 NT$1,299。位於台北中山區。特色：龍蝦、天使紅蝦、握壽司。",
                "meta": {"name": "三燔本家", "rating": 4.6, "location": "台北中山區", "category": "日式 Buffet"}
            },
            {
                "id": "r2",
                "doc": "台北君悅凱菲屋 - 評分 4.5 顆星，晚餐 NT$2,200，午餐 NT$1,800。位於台北信義區。特色：甜點區、 各國料理。",
                "meta": {"name": "台北君悅凱菲屋", "rating": 4.5, "location": "台北信義區", "category": "五星飯店"}
            },
            {
                "id": "r3",
                "doc": "NAGOMI - 評分 4.7 顆星，晚餐 NT$1,690，午餐 NT$1,290。位於新北板橋區。特色：港式燒臘、生魚片。",
                "meta": {"name": "NAGOMI", "rating": 4.7, "location": "新北板橋區", "category": "日式 Buffet"}
            },
            {
                "id": "r4",
                "doc": "漢來海港 - 評分 4.4 顆星，晚餐 NT$1,380，午餐 NT$1,180。位於台北中山區/敦化北路。特色：CP值最高、分店多。",
                "meta": {"name": "漢來海港", "rating": 4.4, "location": "台北中山區", "category": "CP值最高"}
            },
            {
                "id": "r5",
                "doc": "星嶼沙拉吧 - 評分 4.5 顆星，晚餐 NT$888，午餐 NT$788。位於新北三重區。特色：素食友善、創意沙拉。",
                "meta": {"name": "星嶼沙拉吧", "rating": 4.5, "location": "新北三重區", "category": "素食 Buffet"}
            },
            {
                "id": "r6",
                "doc": "涮乃葉 - 評分 4.3 顆星，晚餐 NT$768，午餐 NT$668。位於台北多家分店。特色：日式涮涮鍋、和牛。",
                "meta": {"name": "涮乃葉", "rating": 4.3, "location": "台北多家分店", "category": "日式火鍋"}
            },
            {
                "id": "r7",
                "doc": "燒肉眾 - 評分 4.2 顆星，晚餐 NT$699，午餐 NT$599。位於台北公館/板橋。特色：日式燒肉、吃到飽。",
                "meta": {"name": "燒肉眾", "rating": 4.2, "location": "台北公館", "category": "日式燒肉"}
            },
            {
                "id": "r8",
                "doc": "彩豐樓 - 評分 4.4 顆星，晚餐 NT$1,880，午餐 NT$1,580。位於台北中山區。特色：粵式料理、海鮮。",
                "meta": {"name": "彩豐樓", "rating": 4.4, "location": "台北中山區", "category": "粵式 Buffet"}
            },
            {
                "id": "r9",
                "doc": "旭集 - 評分 4.6 顆星，晚餐 NT$1,690，午餐 NT$1,290。位於台北信義區。特色：日式料理、甜點。",
                "meta": {"name": "旭集", "rating": 4.6, "location": "台北信義區", "category": "日式 Buffet"}
            },
            {
                "id": "r10",
                "doc": "十二廚 - 評分 4.3 顆星，晚餐 NT$2,000，午餐 NT$1,600。位於台北中山區。特色：各國料理、甜點。",
                "meta": {"name": "十二廚", "rating": 4.3, "location": "台北中山區", "category": "五星飯店"}
            },
            {
                "id": "r11",
                "doc": "飪室 - 評分 4.5 顆星，晚餐 NT$699，午餐 NT$599。位於新北新莊區。特色：印度料理、素食友善。",
                "meta": {"name": "飪室", "rating": 4.5, "location": "新北新莊區", "category": "異國料理"}
            }
        ]
        
        print(f'Adding {len(sample_restaurants)} items', flush=True)
        ids = [r["id"] for r in sample_restaurants]
        docs = [r["doc"] for r in sample_restaurants]
        metas = [r["meta"] for r in sample_restaurants]
        col.add(ids=ids, documents=docs, metadatas=metas)
        print(f'Added, count={col.count()}', flush=True)
        
        return jsonify({
            'success': True,
            'message': f'已初始化 {len(sample_restaurants)} 家餐廳，共 {col.count()} 筆資料'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

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
                emb = None
                if i < len(embs) and embs[idx] is not None:
                    try:
                        emb_list = embs[idx]
                        if hasattr(emb_list, 'tolist'):
                            emb_list = emb_list.tolist()
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
        
        formatted = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
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
            <input type="password" id="password" placeholder="請輸入密碼" onkeypress="if(event.key==='\'Enter\'')login()">
        </div>
        <button class="btn" onclick="login()">登入</button>
        <p class="error" id="error">密碼錯誤</p>
    </div>

    <script>
        function login() {
            const password = document.getElementById('password').value;
            localStorage.setItem('admin_auth', password);
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
    # Railway 會設定 PORT 環境變量
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    print(f"Starting server on port {port}, debug={debug}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=debug)
