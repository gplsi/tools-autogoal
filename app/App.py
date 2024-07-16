import os
import logging
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import base64
import websockets
from io import BytesIO

# base URL for AutoGoal API
BASE_URL = os.getenv('SERVER_URL', '127.0.0.1:4239')

# Create a FastAPI instance
app = FastAPI()

# Monta la carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create a Jinja2Templates instance and specify the templates directory
templates = Jinja2Templates(directory="templates")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get('/')
async def index(request: Request):
    # Render the 'index.html' template with the stored messages
    return templates.TemplateResponse("index.html", {"request": request})

# Lista para almacenar los datos recibidos
datos_recibidos = []

# WebSocket endpoint for receiving and broadcasting data
@app.websocket('/exec')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    #logger.info(f"Received message: {data}")
    datos_recibidos.append(data)
    await websocket.send_text(data)
    await websocket.close()

# Ruta para obtener los datos almacenados
@app.get('/datos')
async def obtener_datos():
    if datos_recibidos == []:
        return JSONResponse(content={"message": "No data available"}, status_code=200)
    return datos_recibidos[-4:]

@app.get('/getTrainModels')
async def get_train_models():
    uri = f"ws://{BASE_URL}/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send(b"getTrainModels")
        response = await websocket.recv()
        await websocket.send(b"Finished")
        await websocket.close()
        return response

async def send_text(text_data, info,unique_id):
    uri = f"ws://{BASE_URL}/ws"  # IP address of the FastAPI instance
    async with websockets.connect(uri) as websocket:
        await websocket.send(b"Data")  # Aquí convertimos la cadena "Data" a bytes
        response = await websocket.recv()
        await websocket.send(info.encode('utf-8'))  # Convertimos el texto 'info' a bytes antes de enviarlo
        response = await websocket.recv()
        await websocket.send(unique_id.encode('utf-8')) 
        response = await websocket.recv()
        await websocket.send(text_data)  # Convertimos el texto 'text_data' a bytes antes de enviarlo
        response = await websocket.recv()
        await websocket.close()
        logger.info("Connection closed.")

@app.post('/save_txt')
async def save_txt(request: Request):
    text_data = await request.body()
    file_info = request.headers.get('X-File-Info')
    unique_id = request.headers.get('X-Unique-ID')
    await send_text(text_data, file_info,unique_id)
    return JSONResponse(content={"message": "Data saved successfully"}, status_code=200)

async def send_json(json_data):
    uri = f"ws://{BASE_URL}/ws"
    datos_recibidos.clear()
    async with websockets.connect(uri, extra_headers=[("Content-Type", "application/json")]) as websocket:
        await websocket.send(b"Json")
        response = await websocket.recv()
        json_string = json.dumps(json_data)
        await websocket.send(json_string.encode('utf-8'))
        response = await websocket.recv()
        while response != "Ending connection" and response != "Starting training":
            response = await websocket.recv()
            logger.info(f"{response}")
        await websocket.close()
        logger.info("Connection closed.")

@app.post('/save_json')
async def save_json(request: Request):
    json_data = await request.json()
    await send_json(json_data)
    return JSONResponse(content={"message": "JSON saved successfully"}, status_code=200)

    
async def send_parameters(json_values):
    uri = f"ws://{BASE_URL}/ws"
    async with websockets.connect(uri, extra_headers=[("Content-Type", "application/json")]) as websocket:
        await websocket.send(b"Prediction")
        response = await websocket.recv()
        json_string = json.dumps(json_values)
        await websocket.send(json_string.encode('utf-8'))
        response = await websocket.recv()
        await websocket.send(b"Finished")
        await websocket.close()
        logger.info("Connection closed.")
        return response
    
@app.post('/get_result')
async def get_result(request: Request):
    json_values = await request.json()
    result = await send_parameters(json_values)
    return result

async def get_model():
    uri = f"ws://{BASE_URL}/ws"  # IP address of the FastAPI instance
    async with websockets.connect(uri, extra_headers=[("Content-Type", "application/json")]) as websocket:
        await websocket.send(b"get")
        response = await websocket.recv()
        binary_data = base64.b64decode(response)
        await websocket.send(b"Finished")
        await websocket.close()
        logger.info("Connection closed.")
        return binary_data
    
@app.get('/get_zipmodel')
async def get_zipmodel():
    decoded_zip = await get_model()
    zip_io = BytesIO(decoded_zip)
    return StreamingResponse(zip_io, media_type="application/zip")
    
async def get_old_model(model_name):
    uri = f"ws://{BASE_URL}/ws"  # IP address of the FastAPI instance
    async with websockets.connect(uri) as websocket:
        await websocket.send(b"getOldModel")
        response = await websocket.recv()
        await websocket.send(model_name)
        response = await websocket.recv()
        binary_data = base64.b64decode(response)
        await websocket.send(b"Finished")
        await websocket.close()
        logger.info("Connection closed.")
        return binary_data

@app.post('/getSelectedModel')
async def get_selected_model(request: Request):
    text_data = await request.body()
    decoded_zip = await get_old_model(text_data)
    zip_io = BytesIO(decoded_zip)
    return StreamingResponse(zip_io, media_type="application/zip")


    
    





