import os
import threading

def run_FastAPI_app():
    os.system('cd Router && uvicorn main:app --reload --port 5001')

if __name__ == '__main__':
    run_FastAPI_app_process = threading.Thread(target=run_FastAPI_app)
    run_FastAPI_app_process.start()
    run_FastAPI_app_process.join()

    print('Bot process terminated.')