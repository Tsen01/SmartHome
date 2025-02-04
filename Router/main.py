import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import firebase_admin
from firebase_admin import credentials, db as realtime_db
from databaseURL import databaseURL     # import Firebase Realtime Database 的 URL

# 初始化 Firebase Admin SDK
cred = credentials.Certificate("./json/firebase.json")
options = {
    'databaseURL': databaseURL
}
firebase_admin.initialize_app(cred, options)

app = FastAPI()

# 配置模板
templates = Jinja2Templates(directory="templates")   # 指定 HTML 模板的目錄

# 設定靜態文件資料夾
web_img = "static/img"
app.mount("/img", StaticFiles(directory=web_img), name="Icon")
app.mount("/img", StaticFiles(directory=web_img), name="light_on")
app.mount("/img", StaticFiles(directory=web_img), name="light_off")
app.mount("/img", StaticFiles(directory=web_img), name="bedroom_light_on")
app.mount("/img", StaticFiles(directory=web_img), name="bedroom_light_off")
app.mount("/js", StaticFiles(directory="static/js"), name="light")
app.mount("/js", StaticFiles(directory="static/js"), name="Clock")

# 路由：首頁
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    try:
        # 從 Firebase Realtime Database 取得 LED data
        yled_ref = realtime_db.reference("data/YLED")
        yled_status = yled_ref.get()  # 取得 YLED 的狀態
        rled_ref = realtime_db.reference("data/RLED")
        rled_status = rled_ref.get()  # 取得 RLED 的狀態

        # print YLED and RLED
        print(f"YLED Status: {yled_status}")
        print(f"RLED Status: {rled_status}")

        # 將 LED 的值傳到網頁
        return templates.TemplateResponse(
            "index.html",  # 使用的模板
            {
                "request": request,
                "yled_status": yled_status if yled_status is not None else False,
                "rled_status": rled_status if rled_status is not None else False,
            }
        )
    # 異常處理
    except Exception as e:
        # 輸出錯誤訊息, 並使用 index.html, LED 狀態設為預設值
        print(f"Error fetching Firebase data: {e}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "yled_status": False,
                "rled_status": False,
            }
        )


# 路由：控制燈的開關 (POST請求)
# 路由：控制燈的開關 (POST請求)
@app.post("/control_light", response_class=HTMLResponse)
async def control_light(request: Request, light_name: str = Form(...), status: bool = Form(...)):
    try:
        # 根據提交的燈的名稱更新 Firebase 中相對應的燈的狀態
        if light_name == "YLED":
            yled_ref = realtime_db.reference("data/YLED")
            yled_ref.set(status)  # 設置燈的狀態
        elif light_name == "RLED":
            rled_ref = realtime_db.reference("data/RLED")
            rled_ref.set(status)  # 設置燈的狀態

        # 完成後返回主頁，並傳遞最新的燈狀態
        return read_root(request)
    except Exception as e:
        print(f"Error updating Firebase data: {e}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "yled_status": False,
                "rled_status": False,
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001)