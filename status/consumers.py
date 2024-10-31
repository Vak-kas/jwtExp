import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import requests
import channels

class MetricsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # 주기적으로 클라이언트에게 데이터를 전송하는 루프 실행
        self.send_task = asyncio.create_task(self.send_metrics_periodically())

    async def disconnect(self, close_code):
        # 연결 해제 시 주기적인 작업 중지
        if hasattr(self, 'send_task'):
            self.send_task.cancel()

    async def send_metrics_periodically(self):
        try:
            while True:
                response = requests.get('http://localhost:9090/api/v1/query', params={
                    'query': 'node_cpu_seconds_total'
                })
                data = response.json()

                # 프론트엔드에 JSON 데이터 전송
                await self.send(text_data=json.dumps({
                    "metrics": data['data']['result']
                }))

                # 5초마다 데이터를 전송 (원하는 주기에 맞게 조정 가능)
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass  # 작업이 중단될 때 예외 처리
