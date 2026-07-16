# FastAPI on Render

這是一個簡單的 FastAPI 專案，旨在部署到 Render 雲端平台並回傳 "Hello"。

## 專案結構
- [main.py](file:///c:/Users/User/Desktop/render_test/main.py): FastAPI 主程式。
- [requirements.txt](file:///c:/Users/User/Desktop/render_test/requirements.txt): 專案相依套件清單。

## 本地端運行方式

1. 建立並啟用虛擬環境（可選，但建議）：
   ```bash
   python -m venv venv
   # Windows 啟用虛擬環境
   .\venv\Scripts\activate
   # macOS/Linux 啟用虛擬環境
   source venv/bin/activate
   ```

2. 安裝相依套件：
   ```bash
   pip install -r requirements.txt
   ```

3. 啟動伺服器：
   ```bash
   uvicorn main:app --reload
   ```
   啟動後，可以在瀏覽器中開啟 `http://127.0.0.1:8000` 查看 API 回傳結果，或是 `http://127.0.0.1:8000/docs` 查看自動產生的 API 文件。

## 部署到 Render 的步驟

1. 將此專案推送（Push）到您的 GitHub 儲存庫（Repository）。
2. 登入 [Render 官方網站](https://render.com/)。
3. 點擊 **New** -> **Web Service**。
4. 連結您的 GitHub 帳號並選擇此專案的儲存庫。
5. 設定 Web Service：
   - **Name**: 您的服務名稱（例如 `my-fastapi-hello`）。
   - **Language**: `Python 3`。
   - **Branch**: `main`（或您推送的分支）。
   - **Build Command**: `pip install -r requirements.txt`。
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`（Render 會自動注入 `PORT` 環境變數）。
6. 點擊 **Create Web Service** 進行部署。
