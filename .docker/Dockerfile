FROM python:3
ENV SERVER_TYPE=p2p
ENV PORT=50051
COPY . /grpc-signalc
WORKDIR /grpc-signalc
# setup library
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# generate protobuf
# python -m grpc_tools.protoc -I=. signalc.proto --python_out=. --grpc_python_out=.
RUN sh proto/generate.sh
# start application
EXPOSE $PORT
CMD if [ "$SERVER_TYPE" = "group" ] ; then python ./server_group.py ; else  python ./server.py ; fi