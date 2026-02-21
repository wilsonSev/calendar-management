"""gRPC client for Scheduler service"""
import grpc
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from lib.router.proto.router import router_pb2, router_pb2_grpc
from config import SCHEDULER_HOST, SCHEDULER_PORT


class SchedulerClient:
    """Client for interacting with Scheduler gRPC service"""
    
    def __init__(self, host: str = SCHEDULER_HOST, port: str = SCHEDULER_PORT):
        self.address = f"{host}:{port}"
        self.channel = None
        self.stub = None
    
    def connect(self):
        """Establish connection to the gRPC server"""
        self.channel = grpc.insecure_channel(self.address)
        self.stub = router_pb2_grpc.SchedulerStub(self.channel)
        print(f"Connected to Scheduler service at {self.address}")
    
    def close(self):
        """Close the gRPC channel"""
        if self.channel:
            self.channel.close()
            print("Connection closed")
    
    def create_event(
        self,
        title: str,
        description: str,
        user_id: str,
        start_time: datetime,
        end_time: datetime,
        participants: list[str] = None
    ) -> tuple[bool, str]:
        """
        Create an event in the scheduler
        
        Args:
            title: Event title
            description: Event description
            user_id: User ID
            start_time: Event start datetime
            end_time: Event end datetime
            participants: List of participant emails/IDs
        
        Returns:
            Tuple of (success: bool, event_id: str)
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        # Convert datetime to protobuf Timestamp
        start_timestamp = Timestamp()
        start_timestamp.FromDatetime(start_time)
        
        end_timestamp = Timestamp()
        end_timestamp.FromDatetime(end_time)
        
        # Create request
        request = router_pb2.CreateEventRequest(
            title=title,
            description=description,
            user_id=user_id,
            participants=participants or [],
            datetime=router_pb2.DateTimeRange(
                start_datetime=start_timestamp,
                end_datetime=end_timestamp
            )
        )
        
        try:
            response = self.stub.CreateEvent(request)
            return response.success, response.id
        except grpc.RpcError as e:
            print(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
    def create_task(
        self,
        title: str,
        description: str,
        user_id: str
    ) -> tuple[bool, str]:
        """
        Create a task in the scheduler
        
        Args:
            title: Task title
            description: Task description
            user_id: User ID
        
        Returns:
            Tuple of (success: bool, task_id: str)
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        request = router_pb2.CreateTaskRequest(
            title=title,
            description=description,
            user_id=user_id
        )
        
        try:
            response = self.stub.CreateTask(request)
            return response.success, response.id
        except grpc.RpcError as e:
            print(f"gRPC error: {e.code()} - {e.details()}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
