from concurrent import futures
import logging
import grpc
from proto import signalc_group_pb2
from proto import signalc_group_pb2_grpc
from queue import Queue

group_store = {}

class ClientGroupKey:
    def __init__(self, client_id, device_id, sender_key_distribution):
        self.client_id = client_id
        self.device_id = device_id
        self.sender_key_distribution = sender_key_distribution


class GroupKeyDistribution(signalc_group_pb2_grpc.GroupSenderKeyDistributionServicer):
    def __init__(self):
        self.queues = {}

    def RegisterSenderKeyGroup(self, request, context):
        print('***** CLIENT JOIN GROUP *****')
        print(request)
        client_group_key = ClientGroupKey(request.clientId, request.deviceId, request.senderKeyDistribution)
        if request.groupId not in group_store:
            group_store[request.groupId] = []

        group_store[request.groupId].append(client_group_key)
        return signalc_group_pb2.BaseResponse(message='success')

    def GetSenderKeyInGroup(self, request, context):
        group_id = request.groupId
        client_id = request.senderId
        clients_in_group = group_store[group_id]

        for client in clients_in_group:
            if client.client_id == client_id:
                response = signalc_group_pb2.GroupGetSenderKeyResponse(
                    groupId=group_id,
                    senderKey=signalc_group_pb2.GroupSenderKeyObject(
                        senderId=client.client_id,
                        deviceId=client.device_id,
                        senderKeyDistribution=client.sender_key_distribution
                    )
                )
                return response


    def GetAllSenderKeyInGroup(self, request, context):
        group_id = request.groupId
        clients_in_group = group_store[group_id]
        clients_response = []
        for client in clients_in_group:
            senderKey=signalc_group_pb2.GroupSenderKeyObject(
                senderId=client.client_id,
                deviceId=client.device_id,
                senderKeyDistribution=client.sender_key_distribution
            )
            clients_response.append(senderKey)

        response = signalc_group_pb2.GroupGetAllSenderKeyResponse(
            groupId=group_id,
            allSenderKey=clients_response
        )
        return response

    def Publish(self, request, context):
        group_id = request.groupId
        clients_in_group = group_store[group_id]
        for client in clients_in_group:
            if client.client_id != request.senderId:
                self.queues[client.client_id].put(request)
        return signalc_group_pb2.BaseResponse(message='success')

    def Listen(self, request, context):
        if request.clientId in self.queues:
            while True:
                publication = self.queues[request.clientId].get()  # blocking until the next .put for this queue
                publication_response = signalc_group_pb2.GroupPublication(message=publication.message, senderId=publication.senderId, groupId=publication.groupId)
                yield publication_response

    def Subscribe(self, request, context):
        self.queues[request.clientId] = Queue()
        return signalc_group_pb2.BaseResponse(message='success')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    signalc_group_pb2_grpc.add_GroupSenderKeyDistributionServicer_to_server(GroupKeyDistribution(), server)
    server.add_insecure_port('0.0.0.0:50052')
    server.start()
    print('Server has started at port: 50052')
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
