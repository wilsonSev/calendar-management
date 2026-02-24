"""Mock Scheduler gRPC server for testing"""
import grpc
from concurrent import futures
from datetime import datetime

from lib.router.proto.router import router_pb2, router_pb2_grpc


class MockSchedulerServicer(router_pb2_grpc.SchedulerServicer):
    """Mock implementation of Scheduler service"""
    
    def __init__(self):
        self.events = []
        self.tasks = []
        self.event_counter = 1
        self.task_counter = 1
        print("✓ Mock Scheduler initialized\n")
    
    def CreateEvent(self, request, context):
        """
        Mock CreateEvent - just logs and returns success
        
        Args:
            request: CreateEventRequest
            context: gRPC context
        
        Returns:
            CreateEventResponse with success=True
        """
        event_id = f"mock_event_{self.event_counter}"
        self.event_counter += 1
        
        print(f"\n{'='*70}")
        print(f"📅 CreateEvent Request Received")
        print(f"{'='*70}")
        print(f"Event ID: {event_id}")
        print(f"Title: {request.title}")
        print(f"Description: {request.description}")
        print(f"User ID: {request.user_id}")
        print(f"Participants: {', '.join(request.participants) if request.participants else 'None'}")
        
        # Check which time field is set
        if request.HasField('datetime'):
            start_dt = request.datetime.start_datetime.ToDatetime()
            end_dt = request.datetime.end_datetime.ToDatetime()
            print(f"Start: {start_dt}")
            print(f"End: {end_dt}")
            print(f"Duration: {end_dt - start_dt}")
        elif request.HasField('date'):
            start_date = request.date.start_date.ToDatetime()
            end_date = request.date.end_date.ToDatetime()
            print(f"Start Date: {start_date.date()}")
            print(f"End Date: {end_date.date()}")
        
        print(f"{'='*70}\n")
        
        # Store event
        self.events.append({
            'id': event_id,
            'title': request.title,
            'description': request.description,
            'user_id': request.user_id,
            'timestamp': datetime.now()
        })
        
        print(f"✓ Event stored (total events: {len(self.events)})\n")
        
        # Return success
        return router_pb2.CreateEventResponse(
            success=True,
            id=event_id
        )
    
    def CreateTask(self, request, context):
        """
        Mock CreateTask - just logs and returns success
        
        Args:
            request: CreateTaskRequest
            context: gRPC context
        
        Returns:
            CreateTaskResponse with success=True
        """
        task_id = f"mock_task_{self.task_counter}"
        self.task_counter += 1
        
        print(f"\n{'='*70}")
        print(f"✅ CreateTask Request Received")
        print(f"{'='*70}")
        print(f"Task ID: {task_id}")
        print(f"Title: {request.title}")
        print(f"Description: {request.description}")
        print(f"User ID: {request.user_id}")
        print(f"{'='*70}\n")
        
        # Store task
        self.tasks.append({
            'id': task_id,
            'title': request.title,
            'description': request.description,
            'user_id': request.user_id,
            'timestamp': datetime.now()
        })
        
        print(f"✓ Task stored (total tasks: {len(self.tasks)})\n")
        
        # Return success
        return router_pb2.CreateTaskResponse(
            success=True,
            id=task_id
        )
    
    def print_stats(self):
        """Print statistics"""
        print(f"\n{'='*70}")
        print(f"📊 Mock Scheduler Statistics")
        print(f"{'='*70}")
        print(f"Total Events: {len(self.events)}")
        print(f"Total Tasks: {len(self.tasks)}")
        print(f"{'='*70}\n")


def serve(port=50051):
    """Start mock gRPC server"""
    servicer = MockSchedulerServicer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    router_pb2_grpc.add_SchedulerServicer_to_server(servicer, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    print(f"\n{'='*70}")
    print(f"🎭 Mock Scheduler gRPC Server")
    print(f"{'='*70}")
    print(f"Port: {port}")
    print(f"Status: Running")
    print(f"{'='*70}\n")
    print("This is a MOCK server - it doesn't create real events!")
    print("It just logs requests and returns success.\n")
    print("Waiting for requests from your microservice...")
    print("Press Ctrl+C to stop and see statistics\n")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...\n")
        servicer.print_stats()
        
        if servicer.events:
            print("Last 5 events:")
            for event in servicer.events[-5:]:
                print(f"  - {event['id']}: {event['title']} (user: {event['user_id']})")
        
        if servicer.tasks:
            print("\nLast 5 tasks:")
            for task in servicer.tasks[-5:]:
                print(f"  - {task['id']}: {task['title']} (user: {task['user_id']})")
        
        print("\n")
        server.stop(0)


if __name__ == '__main__':
    serve()
