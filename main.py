import os

import deepl
import firebase_admin
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from firebase_admin import credentials, firestore

DEEPL_AUTH_KEY = os.environ.get("DEEPL_AUTH_KEY")
DEFAULT_URL = "https://www.google.com/search?q=%s"
DEFAULT_QUERY = "こんにちは、世界"

# Use a service account
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/search")
def search(site: str = "google", q: str = ""):
    # 空文字だとエラーになるので、デフォルト値を設定する
    if q == "":
        q = DEFAULT_QUERY
    # DeepLで翻訳
    translator = deepl.Translator(DEEPL_AUTH_KEY)
    translated = translator.translate_text(q, target_lang="EN-US")
    # 検索サイトのURLをfirestoreから取得
    sites_ref = db.collection("sites").get()
    sites = {s.id: s.to_dict() for s in sites_ref}
    url = sites.get(site, {}).get("url", "")
    if url == "":
        url = DEFAULT_URL
    url = url.replace("%s", translated.text)

    return RedirectResponse(url=url)
