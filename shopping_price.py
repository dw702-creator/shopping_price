# app.py
import streamlit as st
from PIL import Image
import os
import numpy as np

import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.models import Model

import pickle


# -----------------------------
# 설정
# -----------------------------
IMAGE_DB_DIR = "image_db"         # 상품 이미지 저장 디렉토리
METADATA_FILE = "metadata.pkl"    # {"item_key": {"name": ..., "url": ..., "price": ...}}
TOP_K = 10                        # 이미지 유사도로 먼저 고를 후보 개수


# -----------------------------
# Feature Extractor
# -----------------------------
base_model = ResNet50(weights="imagenet", include_top=False, pooling="avg")
model = Model(inputs=base_model.input, outputs=base_model.output)


def get_embedding(img: Image.Image) -> np.ndarray:
    img = img.resize((224, 224))
    x = keras_image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    feat = model.predict(x)
    feat = feat.flatten()
    feat = feat / np.linalg.norm(feat)   # 정규화
    return feat


# -----------------------------
# 상품 DB 로딩
# -----------------------------
@st.cache_data
def load_db():
    embeddings = {}
    meta = {}

    # 메타데이터 로드
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "rb") as f:
            meta = pickle.load(f)

    # 이미지 embedding 계산
    for fname in os.listdir(IMAGE_DB_DIR):
        if fname.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(IMAGE_DB_DIR, fname)
            img = Image.open(path).convert("RGB")
            emb = get_embedding(img)
            key = os.path.splitext(fname)[0]
            embeddings[key] = emb

    return embeddings, meta


# -----------------------------
# 유사도 기반 후보 선택
# -----------------------------
def get_top_similar(query_emb, db_embeddings, k=10):
    scores = []
    for key, emb in db_embeddings.items():
        sim = float(np.dot(query_emb, emb))
        scores.append((key, sim))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return scores[:k]


# -----------------------------
# Streamlit 메인 앱
# -----------------------------
def main():
    st.title("상품 이미지 검색 + 가격 낮은 순 링크 추천")

    uploaded_file = st.file_uploader("검색할 상품 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="업로드된 이미지", use_column_width=True)

        query_emb = get_embedding(img)
        db_embeddings, metadata = load_db()

        # 1) 이미지 유사도 기반 Top-K 후보 추출
        similar_items = get_top_similar(query_emb, db_embeddings, k=TOP_K)

        # 2) 가격 낮은 순으로 재정렬
        ranked_by_price = []
        for key, sim in similar_items:
            info = metadata.get(key, {})
            name = info.get("name", key)
            url = info.get("url", "#")
            price = info.get("price", None)
            ranked_by_price.append({
                "key": key,
                "similarity": sim,
                "name": name,
                "url": url,
                "price": price
            })

        # 가격이 있는 상품만 가격 오름차순 정렬
        ranked_by_price = sorted(ranked_by_price, key=lambda x: x["price"] if x["price"] is not None else float("inf"))

        st.subheader("가격이 낮은 순 추천 상품")

        for item in ranked_by_price:
            st.write(f"### {item['name']}")
            st.write(f"- 가격: **{item['price']}원**" if item['price'] is not None else "- 가격 정보 없음")
            st.write(f"- 유사도 점수: {item['similarity']:.3f}")
            st.write(f"- [상품 링크 열기]({item['url']})")

            # 썸네일 이미지 표시
            image_path = os.path.join(IMAGE_DB_DIR, f"{item['key']}.jpg")
            if not os.path.exists(image_path):
                image_path = os.path.join(IMAGE_DB_DIR, f"{item['key']}.png")
            if os.path.exists(image_path):
                st.image(image_path, width=200)


if __name__ == "__main__":
    main()
