"""gRPC server for Analyzer service"""
import grpc
from concurrent import futures
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp

from lib.analyzer.v1 import analyzer_pb2, analyzer_pb2_grpc
from scheduler_client import SchedulerClient
from message import Message
import openrouter


class AnalyzerServicer(analyzer_pb2_grpc.AnalyzerServiceServicer):
    """Implementation of AnalyzerService"""
    
    def __init__(self):
        self.scheduler_client = SchedulerClient()
        self.scheduler_client.connect()
        print("✓ Connected to Scheduler service")
    
    def AnalyzeText(self, request, context):
        """
        Analyze text and create event in scheduler
        
        Args:
            request: AnalyzeTextRequest with user text
            context: gRPC context
        
        Returns:
            AnalyzeTextResponse with result
        """
        print(f"\n{'='*60}")
        print(f"Received request from user {request.tg_user_id}")
        print(f"Text: {request.text}")
        print(f"Timezone: {request.timezone}")
        print(f"{'='*60}\n")
        
        try:
            # Parse message using OpenRouter LLM
            print("→ Parsing text with OpenRouter LLM...")
            add_info = Message(datetime.now(), f"user_{request.tg_user_id}")
            parsed_event = openrouter.parse_message(request.text, add_info)
            
            print(f"✓ Parsed event: {parsed_event.name}")
            print(f"  Start: {parsed_event.start_time}")
            print(f"  End: {parsed_event.finish_time}\n")
            
            # Create event in Scheduler
            print("→ Creating event in Scheduler...")
            success, event_id = self.scheduler_client.create_event(
                title=parsed_event.name,
                description=f"Created from Telegram by user {request.tg_user_id}",
                user_id=str(request.tg_user_id),
                start_time=parsed_event.start_time,
                end_time=parsed_event.finish_time,
                participants=[]
            )
            
            if success:
                print(f"✓ Event created successfully! ID: {event_id}\n")
                
                # Convert datetime to protobuf Timestamp
                start_ts = Timestamp()
                start_ts.FromDatetime(parsed_event.start_time)
                
                end_ts = Timestamp()
                end_ts.FromDatetime(parsed_event.finish_time)
                
                # Return success response
                return analyzer_pb2.AnalyzeTextResponse(
                    create_event=analyzer_pb2.CreateEvent(
                        title=parsed_event.name,
                        description=f"Event ID: {event_id}",
                        start_time=start_ts,
                        end_time=end_ts
                    )
                )
            else:
                print(f"✗ Failed to create event\n")
                return analyzer_pb2.AnalyzeTextResponse(
                    error=analyzer_pb2.Error(
                        message="Failed to create event in scheduler"
                    )
                )
        
        except Exception as e:
            print(f"✗ Error: {e}\n")
            return analyzer_pb2.AnalyzeTextResponse(
                error=analyzer_pb2.Error(
                    message=f"Error processing request: {str(e)}"
                )
            )
    
    def __del__(self):
        """Cleanup on shutdown"""
        if hasattr(self, 'scheduler_client'):
            self.scheduler_client.close()


def serve(port=50053):
    """Start gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    analyzer_pb2_grpc.add_AnalyzerServiceServicer_to_server(
        AnalyzerServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    print(f"\n{'='*60}")
    print(f"Analyzer gRPC Server started on port {port}")
    print(f"{'='*60}\n")
    print("Waiting for requests...")
    print("Press Ctrl+C to stop\n")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        server.stop(0)


if __name__ == '__main__':
    serve()
