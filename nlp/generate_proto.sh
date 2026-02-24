#!/bin/bash

# Script to generate Python code from proto files

PROTO_DIR="../proto"
OUT_DIR="./lib"

echo "Generating Python code from proto files..."

# Generate for scheduler/router service
./venv/bin/python -m grpc_tools.protoc \
    -I${PROTO_DIR} \
    --python_out=${OUT_DIR} \
    --grpc_python_out=${OUT_DIR} \
    --pyi_out=${OUT_DIR} \
    ${PROTO_DIR}/router/proto/router/router.proto

if [ $? -ne 0 ]; then
    echo "✗ Error generating router proto files"
    exit 1
fi

# Generate for analyzer service
./venv/bin/python -m grpc_tools.protoc \
    -I${PROTO_DIR} \
    --python_out=${OUT_DIR} \
    --grpc_python_out=${OUT_DIR} \
    --pyi_out=${OUT_DIR} \
    ${PROTO_DIR}/analyzer/v1/analyzer.proto

if [ $? -ne 0 ]; then
    echo "✗ Error generating analyzer proto files"
    exit 1
fi

# Create __init__.py files for proper package structure
touch ${OUT_DIR}/router/__init__.py
touch ${OUT_DIR}/router/proto/__init__.py
touch ${OUT_DIR}/router/proto/router/__init__.py

# Fix imports in generated gRPC file (change absolute to relative imports)
ROUTER_GRPC_FILE="${OUT_DIR}/router/proto/router/router_pb2_grpc.py"
if [ -f "$ROUTER_GRPC_FILE" ]; then
    sed -i.bak 's/from router\.proto\.router import router_pb2/from . import router_pb2/g' "$ROUTER_GRPC_FILE"
    rm "${ROUTER_GRPC_FILE}.bak"
    echo "✓ Fixed imports in router gRPC file"
fi

ANALYZER_GRPC_FILE="${OUT_DIR}/analyzer/v1/analyzer_pb2_grpc.py"
if [ -f "$ANALYZER_GRPC_FILE" ]; then
    sed -i.bak 's/from analyzer\.v1 import analyzer_pb2/from . import analyzer_pb2/g' "$ANALYZER_GRPC_FILE"
    rm "${ANALYZER_GRPC_FILE}.bak"
    echo "✓ Fixed imports in analyzer gRPC file"
fi

echo "✓ Proto files generated successfully!"
