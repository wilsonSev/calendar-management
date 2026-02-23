import asyncio
import logging
import sys
import os
from concurrent import futures
import grpc
from datetime import datetime

# from proto.analyzer.v1 import analyzer_pb2
# from proto.analyzer.v1 import analyzer_pb2_grpc
import sys
import os

# Добавляем путь к сгенерированному коду
sys.path.append(os.path.join(os.path.dirname(__file__), 'gen'))

try:
    from proto.analyzer.v1 import analyzer_pb2
    from proto.analyzer.v1 import analyzer_pb2_grpc
except ImportError:
    # Fallback for direct execution
    import analyzer_pb2
    import analyzer_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

import openrouter
from message import Message

class AnalyzerService(analyzer_pb2_grpc.AnalyzerServiceServicer):
    def AnalyzeText(self, request, context):
        logging.info(f"Received analysis request: {request.text}")
        
        # Construct the context message for the analyzer
        # Note: We rely on the server's local time for now, but should eventually use request.timezone
        msg_info = Message(
            sent=datetime.now(), 
            user=f"User_{request.tg_user_id}" # We don't have the name in the proto yet
        )
        
        try:
            event = openrouter.parse_message(request.text, msg_info)
            
            # Convert python Event to proto CreateEvent
            start_ts = Timestamp()
            start_ts.FromDatetime(event.start_time)
            
            end_ts = Timestamp()
            end_ts.FromDatetime(event.finish_time)
            
            create_event = analyzer_pb2.CreateEvent(
                title=event.name,
                description="", # Description is not parsed right now
                start_time=start_ts,
                end_time=end_ts
            )
            
            return analyzer_pb2.AnalyzeTextResponse(create_event=create_event)
            
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            return analyzer_pb2.AnalyzeTextResponse(
                error=analyzer_pb2.Error(message=str(e))
            )

def serve():
    # Use NLP_PORT or GRPC_PORT, fallback to 50051. Avoid generic PORT which might be used by Gateway
    port = os.getenv("NLP_PORT", os.getenv("GRPC_PORT", "50051"))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analyzer_pb2_grpc.add_AnalyzerServiceServicer_to_server(AnalyzerService(), server)
    server.add_insecure_port(f'[::]:{port}')
    logging.info(f"Server started, listening on {port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        serve()
    except KeyboardInterrupt:
        pass
