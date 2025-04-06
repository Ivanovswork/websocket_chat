import time
import json
from locust import User, TaskSet, task, between
import websocket
from locust import events

# Глобальная переменная для хранения начала временной метки
start_time = None
ws = None


# Событие для фиксации времени ответа
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception=None, start_time=start_time):
    if exception:
        print(f"Request failed: {exception}")


class WebSocketUser(User):
    wait_time = between(0.5, 2)  # Задержка между задачами (в секундах)

    def on_start(self):
        # Получаем ID отправителя и получателя (можно параметризовать)
        self.sender_id = 2
        self.recipient_id = 3
        global ws
        # Создаем WebSocket соединение
        try:
            ws = websocket.create_connection(f"ws://localhost:8000/ws/chat/{self.sender_id}/{self.recipient_id}/") # Замените URL
            print("WebSocket connection established")
        except Exception as e:
            print(f"Error connecting to WebSocket: {e}")
            raise e

    def on_stop(self):
        # Закрываем WebSocket соединение
        global ws
        if ws:
            ws.close()
            print("WebSocket connection closed")

    @task
    def send_message(self):
        global ws
        global start_time

        # Формируем сообщение
        message = {
            "message": f"Hello from Locust {time.time()}"
        }
        message_json = json.dumps(message)
        start_time = time.time()  # Фиксируем время отправки
        # Отправляем сообщение
        try:
            ws.send(message_json)

            # Получаем ответ
            result = ws.recv()

            # Фиксируем время получения ответа
            end_time = time.time()

            # Вычисляем время ответа
            response_time = (end_time - start_time) * 1000  # в миллисекундах

            # Регистрируем успешный запрос
            events.request.fire(
                request_type="ws",
                name="send_message ok",
                response_time=response_time,
                response_length=len(result),
                response=result,  # необязательно, но может быть полезно для отладки
                context=None
            )
        except Exception as e:
            # Регистрируем неудачный запрос
            events.request.fire(
                request_type="ws",
                name="send_message not ok",
                response_time=0,
                response_length=0,
                response=None,
                exception=e,
                context=None
            )

