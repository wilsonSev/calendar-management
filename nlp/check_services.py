"""Utility to check the status of gRPC services"""
import grpc
from config import SCHEDULER_HOST, SCHEDULER_PORT


def check_scheduler_service():
    """Check if Scheduler service is reachable"""
    address = f"{SCHEDULER_HOST}:{SCHEDULER_PORT}"
    
    print(f"Checking Scheduler service at {address}...")
    
    try:
        channel = grpc.insecure_channel(address)
        # Try to connect with a short timeout
        grpc.channel_ready_future(channel).result(timeout=5)
        channel.close()
        
        print(f"✓ Scheduler service is reachable at {address}")
        return True
        
    except grpc.FutureTimeoutError:
        print(f"✗ Timeout: Cannot connect to Scheduler service at {address}")
        print("  Make sure the service is running")
        return False
        
    except Exception as e:
        print(f"✗ Error connecting to Scheduler service: {e}")
        return False


def print_config():
    """Print current configuration"""
    print("\nCurrent Configuration:")
    print(f"  SCHEDULER_HOST: {SCHEDULER_HOST}")
    print(f"  SCHEDULER_PORT: {SCHEDULER_PORT}")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("Service Status Check")
    print("=" * 50)
    print()
    
    print_config()
    
    scheduler_ok = check_scheduler_service()
    
    print()
    print("=" * 50)
    
    if scheduler_ok:
        print("✓ All services are reachable!")
        print("\nYou can now run:")
        print("  python example.py")
        print("  python test_connection.py")
        print("  python main.py")
    else:
        print("✗ Some services are not reachable")
        print("\nTroubleshooting:")
        print("1. Start the Scheduler service (Go)")
        print("2. Check .env file for correct host/port")
        print("3. Verify firewall settings")
    
    print("=" * 50)
