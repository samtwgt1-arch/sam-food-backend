#!/usr/bin/env python3
"""
init_db.py - 在後台服務啟動前初始化 ChromaDB 資料
由 entrypoint.sh 在 gunicorn 啟動前呼叫
"""
import os
import sys

# 確保路徑正確
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chromadb
from chromadb.config import Settings

CHROMA_DATA_PATH = '/tmp/chromadb_data'

def init_data():
    print('=== Initializing ChromaDB data ===', flush=True)
    
    os.makedirs(CHROMA_DATA_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    
    # 檢查是否已有資料
    try:
        col = client.get_collection('taipei_food')
        count = col.count()
        if count > 0:
            print(f'Collection already has {count} items, skipping', flush=True)
            return
        client.delete_collection('taipei_food')
        print('Deleted empty collection', flush=True)
    except Exception as e:
        print(f'Collection does not exist: {e}', flush=True)
    
    # 建立 collection（此時 ChromaDB 會快取嵌入模型）
    col = client.create_collection('taipei_food')
    print('Collection created, adding data...', flush=True)
    
    # 12 家台北吃到飽餐廳
    restaurants = [
        ("r0", "探索廚房 - 評分 4.5 顆星，晚餐 NT$2,580，午餐 NT$1,980。位於台北信義區。特色：龍蝦、牛排、帝王蟹。", {"name": "探索廚房", "rating": 4.5, "location": "台北信義區", "category": "頂級 Buffet"}),
        ("r1", "三燔本家 - 評分 4.6 顆星，晚餐 NT$1,499，午餐 NT$1,299。位於台北中山區。特色：龍蝦、天使紅蝦、握壽司。", {"name": "三燔本家", "rating": 4.6, "location": "台北中山區", "category": "日式 Buffet"}),
        ("r2", "台北君悅凱菲屋 - 評分 4.5 顆星，晚餐 NT$2,200，午餐 NT$1,800。位於台北信義區。特色：甜點區、各國料理。", {"name": "台北君悅凱菲屋", "rating": 4.5, "location": "台北信義區", "category": "五星飯店"}),
        ("r3", "NAGOMI - 評分 4.7 顆星，晚餐 NT$1,690，午餐 NT$1,290。位於新北板橋區。特色：港式燒臘、生魚片。", {"name": "NAGOMI", "rating": 4.7, "location": "新北板橋區", "category": "日式 Buffet"}),
        ("r4", "漢來海港 - 評分 4.4 顆星，晚餐 NT$1,380，午餐 NT$1,180。位於台北中山區。特色：CP值最高、分店多。", {"name": "漢來海港", "rating": 4.4, "location": "台北中山區", "category": "CP值最高"}),
        ("r5", "星嶼沙拉吧 - 評分 4.5 顆星，晚餐 NT$888，午餐 NT$788。位於新北三重區。特色：素食友善、創意沙拉。", {"name": "星嶼沙拉吧", "rating": 4.5, "location": "新北三重區", "category": "素食 Buffet"}),
        ("r6", "涮乃葉 - 評分 4.3 顆星，晚餐 NT$768，午餐 NT$668。位於台北多家分店。特色：日式涮涮鍋、和牛。", {"name": "涮乃葉", "rating": 4.3, "location": "台北多家分店", "category": "日式火鍋"}),
        ("r7", "燒肉眾 - 評分 4.2 顆星，晚餐 NT$699，午餐 NT$599。位於台北公館/板橋。特色：日式燒肉、吃到飽。", {"name": "燒肉眾", "rating": 4.2, "location": "台北公館", "category": "日式燒肉"}),
        ("r8", "彩豐樓 - 評分 4.4 顆星，晚餐 NT$1,880，午餐 NT$1,580。位於台北中山區。特色：粵式料理、海鮮。", {"name": "彩豐樓", "rating": 4.4, "location": "台北中山區", "category": "粵式 Buffet"}),
        ("r9", "旭集 - 評分 4.6 顆星，晚餐 NT$1,690，午餐 NT$1,290。位於台北信義區。特色：日式料理、甜點。", {"name": "旭集", "rating": 4.6, "location": "台北信義區", "category": "日式 Buffet"}),
        ("r10", "十二廚 - 評分 4.3 顆星，晚餐 NT$2,000，午餐 NT$1,600。位於台北中山區。特色：各國料理、甜點。", {"name": "十二廚", "rating": 4.3, "location": "台北中山區", "category": "五星飯店"}),
        ("r11", "飪室 - 評分 4.5 顆星，晚餐 NT$699，午餐 NT$599。位於新北新莊區。特色：印度料理、素食友善。", {"name": "飪室", "rating": 4.5, "location": "新北新莊區", "category": "異國料理"}),
    ]
    
    ids = [r[0] for r in restaurants]
    docs = [r[1] for r in restaurants]
    metas = [r[2] for r in restaurants]
    col.add(ids=ids, documents=docs, metadatas=metas)
    print(f'Init complete: {col.count()} items', flush=True)

if __name__ == '__main__':
    init_data()