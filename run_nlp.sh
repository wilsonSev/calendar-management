#!/bin/bash
set -e

# Setup virtual environment
if [ ! -d "nlp/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv nlp/venv
fi

# Activate virtual environment
source nlp/venv/bin/activate

# Install python dependencies
echo "Installing Python dependencies..."
pip install grpcio grpcio-tools python-dotenv requests

# Create output directories
echo "Preparing directories..."
mkdir -p nlp/gen/proto/analyzer/v1
touch nlp/gen/__init__.py
touch nlp/gen/proto/__init__.py
touch nlp/gen/proto/analyzer/__init__.py
touch nlp/gen/proto/analyzer/v1/__init__.py

# Generate gRPC code
echo "Generating gRPC code..."
python3 -m grpc_tools.protoc -I . \
    --python_out=./nlp/gen \
    --grpc_python_out=./nlp/gen \
    proto/analyzer/v1/analyzer.proto

echo "Code generation complete."

# Run the server
echo "Starting gRPC server..."
export PYTHONPATH=$PYTHONPATH:$(pwd)/nlp
python3 nlp/grpc_server.py
