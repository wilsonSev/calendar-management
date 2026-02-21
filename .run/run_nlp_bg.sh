#!/bin/bash
source "/Users/andrepribavkin/calendar-management2/calendar-management/nlp/venv/bin/activate"
export PYTHONPATH="/Users/andrepribavkin/calendar-management2/calendar-management/nlp:$PYTHONPATH"
export NLP_PORT="50052"
exec python3 "/Users/andrepribavkin/calendar-management2/calendar-management/nlp/grpc_server.py"
