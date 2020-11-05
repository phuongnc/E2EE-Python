## Signal Protocol Python
### Features
 1. Sample Chat with End to End Encryption (E2EE) 
 2. Support Peer to Peer (P2P) message and Group message
 3. Using GRPC protobuf

### 1. Requirement
1. Python 3x
2. Google Protobuf
3. Libsignal

### 2. Install libraries
> pip install -r requirements.txt

### 3. Run and test on locally
Generate protobuf
> sh proto/generate.sh

P2P Test
> python server.py
> python client_alice.py
> python client_bob.py

Group Test
> python server_group.py
> python client_group_one.py
> python client_group_two.py
> python client_group_three.py

### 4. Run Server with Docker
P2P server ( server address ***your-ip:50051***)
```sh
 sh .docker/run.docker.sh -p
```
Group server (server address ***your-ip:50052***)
```sh
 sh .docker/run.docker.sh -g
```
