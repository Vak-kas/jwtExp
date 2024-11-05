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
                metrics = {
                    'node_exporter': {},
                    'prometheus': {}
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
                #
                for key, query in node_exporter_queries.items():
                    response = requests.get('http://localhost:9090/api/v1/query', params={'query': query})
                    data = response.json()
                    # print(data)
                    if 'data' in data and 'result' in data['data']:
                        # 최신 값만 추출하여 전송
                        latest_metrics = []
                        for result in data['data']['result']:
                            if 'value' in result:
                                latest_metrics.append(result)
                            elif 'values' in result:
                                latest_metrics.append({
                                    "metric": result["metric"],
                                    "value": result["values"][-1]  # 가장 최신 값만 포함
                                })
                        metrics['node_exporter'][key] = latest_metrics
                    else:
                        metrics['node_exporter'][key] = []

                # Prometheus에서 필요한 메트릭 정의
                prometheus_queries = {
                    'django_http_requests_total_by_method_total': 'django_http_requests_total_by_method_total',
                    'django_http_requests_latency_seconds_by_view_method_sum': 'django_http_requests_latency_seconds_by_view_method_sum',
                    # 'django_http_responses_total_by_status_total': 'django_http_responses_total_by_status_total',
                    'django_http_requests_body_total_bytes_sum': 'django_http_requests_body_total_bytes_sum',
                    'django_http_responses_body_total_bytes_sum': 'django_http_responses_body_total_bytes_sum'
                }

                for key, query in prometheus_queries.items():
                    response = requests.get('http://localhost:9090/api/v1/query', params={'query': query})
                    data = response.json()
                    # print(data)
                    if 'data' in data and 'result' in data['data']:
                        # 최신 값만 추출하여 전송
                        latest_metrics = []
                        for result in data['data']['result']:
                            if 'value' in result:
                                latest_metrics.append(result)
                            elif 'values' in result:
                                latest_metrics.append({
                                    "metric": result["metric"],
                                    "value": result["values"][-1]  # 가장 최신 값만 포함
                                })
                        metrics['prometheus'][key] = latest_metrics
                    else:
                        metrics['prometheus'][key] = []

                        # 프론트엔드에 JSON 데이터 전송
                    await self.send(text_data=json.dumps(metrics))

                    # 5초마다 데이터를 전송 (원하는 주기에 맞게 조정 가능)
                    await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass  # 작업이 중단될 때 예외 처리