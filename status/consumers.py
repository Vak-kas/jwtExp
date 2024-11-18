import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import requests
from collections import defaultdict
import datetime
from asgiref.sync import sync_to_async
from .models import RecordedSession

class MetricsConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()
        self.recording = False
        self.recorded_data = []
        self.start_time = None
        self.ip_request_counts = defaultdict(int)

    async def connect(self):
        await self.accept()
        self.send_task = asyncio.create_task(self.send_metrics_periodically())

    async def disconnect(self, close_code):
        if hasattr(self, 'send_task'):
            self.send_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('command') == 'start_recording':
            self.recording = True
            self.session_name = data.get('session_name', 'Unnamed Session')
            self.start_time = datetime.datetime.now()
            self.recorded_data = []
        elif data.get('command') == 'stop_recording':
            self.recording = False
            end_time = datetime.datetime.now()

            # 비동기적으로 데이터베이스에 녹화된 데이터 저장
            await sync_to_async(RecordedSession.objects.create)(
                session_name=self.session_name,
                start_time=self.start_time,
                end_time=end_time,
                data=self.recorded_data
            )
        elif data.get('command') == 'get_recording':
            session_id = data.get('session_id')
            if session_id:
                session = await sync_to_async(RecordedSession.objects.get)(id=session_id)
                await self.send(text_data=json.dumps({'recorded_data': session.data}))

    async def send_metrics_periodically(self):
        try:
            while True:
                metrics = {
                    'node_exporter': {},
                    'prometheus': {},
                    'ip_requests': self.ip_request_counts  # IP 요청 수 전송
                }

                # node_exporter에서 메트릭 가져오기
                node_exporter_queries = {
                    'cpu_usage': '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
                    'cpu_core_usage': 'avg by (cpu) (rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100',
                    'load_average_1': 'node_load1',
                    'load_average_5': 'node_load5',
                    'load_average_15': 'node_load15',
                    'memory_total': 'node_memory_MemTotal_bytes',
                    'memory_used': 'node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes',
                    'disk_read_write': 'rate(node_disk_read_bytes_total[5m]) + rate(node_disk_written_bytes_total[5m])',
                    'network_receive': 'rate(node_network_receive_bytes_total[5m])',
                    'network_transmit': 'rate(node_network_transmit_bytes_total[5m])',
                    'uptime': 'node_time_seconds - node_boot_time_seconds',
                    'reboots': 'changes(node_boot_time_seconds[1h])'
                }

                for key, query in node_exporter_queries.items():
                    response = requests.get('http://localhost:9090/api/v1/query', params={'query': query})
                    data = response.json()
                    latest_metrics = []
                    if 'data' in data and 'result' in data['data']:
                        for result in data['data']['result']:
                            if 'value' in result:
                                latest_metrics.append(result)
                            elif 'values' in result:
                                latest_metrics.append({
                                    "metric": result["metric"],
                                    "value": result["values"][-1]
                                })
                        metrics['node_exporter'][key] = latest_metrics
                    else:
                        metrics['node_exporter'][key] = []

                # Prometheus 메트릭 수집
                prometheus_queries = {
                    'django_http_requests_total_by_method_total': 'django_http_requests_total_by_method_total',
                    'django_http_requests_latency_seconds_by_view_method_sum': 'django_http_requests_latency_seconds_by_view_method_sum',
                    'django_http_requests_body_total_bytes_sum': 'django_http_requests_body_total_bytes_sum',
                    'django_http_responses_body_total_bytes_sum': 'django_http_responses_body_total_bytes_sum'
                }

                for key, query in prometheus_queries.items():
                    response = requests.get('http://localhost:9090/api/v1/query', params={'query': query})
                    data = response.json()
                    latest_metrics = []
                    if 'data' in data and 'result' in data['data']:
                        for result in data['data']['result']:
                            if 'value' in result:
                                latest_metrics.append(result)
                            elif 'values' in result:
                                latest_metrics.append({
                                    "metric": result["metric"],
                                    "value": result["values"][-1]
                                })
                        metrics['prometheus'][key] = latest_metrics
                    else:
                        metrics['prometheus'][key] = []

                # 연결된 클라이언트의 IP 주소를 수집
                ip_address = self.scope['client'][0]
                self.ip_request_counts[ip_address] += 1

                # 녹화 중이면 데이터를 저장
                if self.recording:
                    current_time = datetime.datetime.now()
                    elapsed_time = (current_time - self.start_time).total_seconds()
                    self.recorded_data.append({'time': elapsed_time, 'metrics': metrics})

                # 프론트엔드에 JSON 데이터 전송
                await self.send(text_data=json.dumps(metrics))

                # 5초마다 데이터를 전송 (원하는 주기에 맞게 조정 가능)
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass  # 작업이 중단될 때 예외 처리
