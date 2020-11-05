from __future__ import print_function
import grpc
import threading
from proto import signalc_group_pb2, signalc_group_pb2_grpc
from libsignal.axolotladdress import AxolotlAddress
from libsignal.groups.senderkeyname import SenderKeyName
from store.mysenderkeystore import MySenderKeyStore
from libsignal.groups.groupsessionbuilder import GroupSessionBuilder
from libsignal.groups.groupcipher import GroupCipher
from libsignal.protocol.senderkeydistributionmessage import SenderKeyDistributionMessage

#SENDER_ADDRESS = AxolotlAddress("+14150001111", 1)
#GROUP_SENDER = SenderKeyName("test_group", SENDER_ADDRESS);

class ClientGroupTest:
    def __init__(self, client_id, device_id, host, port):
        self.client_id = client_id
        self.device_id = device_id
        self.stub = self.grpc_stub(host, port)
        self.my_sender_store = MySenderKeyStore()
        self.my_sender_address = AxolotlAddress(client_id, device_id)
        self.listen()

    def grpc_stub(self, host, port):
        channel = grpc.insecure_channel(host + ':' + str(port))
        return signalc_group_pb2_grpc.GroupSenderKeyDistributionStub(channel)

    def register_group_keys(self, group_id):
        group_sender = SenderKeyName(group_id, self.my_sender_address);
        self.my_session_builder = GroupSessionBuilder(self.my_sender_store)
        my_sender_distribution_message = self.my_session_builder.create(group_sender)

        response = self.stub.RegisterSenderKeyGroup(signalc_group_pb2.GroupRegisterSenderKeyRequest(
            groupId=group_sender.groupId,
            clientId=self.client_id,
            deviceId=self.device_id,
            senderKeyDistribution=my_sender_distribution_message.serialize()
        ))
        print("REGISTER SENDER KEY GROUP RESPONSE: " + response.message)

    def listen(self):
        threading.Thread(target=self.heard, daemon=True).start()

    def heard(self):
        request = signalc_group_pb2.GroupSubscribeAndListenRequest(clientId=self.client_id)
        for publication in self.stub.Listen(request):  # this line will wait for new messages from the server
            print("publication=", publication)
            message_plain_text = self.decrypt_message(publication.message, publication.senderId, publication.groupId)
            print("From {}: {}".format(publication.senderId, message_plain_text))

    def subscribe(self):
        request = signalc_group_pb2.GroupSubscribeAndListenRequest(clientId=self.client_id)
        response = self.stub.Subscribe(request)

    def publish(self, message, group_id):
        # encrypt message first
        out_goging_message = self.encrypt_message(message, group_id)
        # send message
        request = signalc_group_pb2.GroupPublishRequest(senderId=self.client_id, groupId=group_id, message=out_goging_message)
        response = self.stub.Publish(request)

    def encrypt_message(self, message, group_id):
        group_sender = SenderKeyName(group_id, self.my_sender_address)
        my_group_cipher = GroupCipher(self.my_sender_store, group_sender)
        out_going_message = my_group_cipher.encrypt(message)
        #out_goging_message_serialize = out_going_message.serialize()
        print("Encrypt Message - Out Going Message =", out_going_message)
        # return encrypt message
        return out_going_message

    def decrypt_message(self, message, sender_id, group_id):
        print("Decrypt Message - In Coming Message Encrypted=", message)
        #get sender key first
        request = signalc_group_pb2.GroupGetSenderKeyRequest(groupId=group_id, senderId=sender_id)
        response = self.stub.GetSenderKeyInGroup(request)
        received_sender_distribution_message = SenderKeyDistributionMessage(serialized=response.senderKey.senderKeyDistribution);

        sender_address = AxolotlAddress(response.senderKey.senderId, response.senderKey.deviceId)
        group_sender = SenderKeyName(group_id, sender_address)
        senderKeyRecord = self.my_sender_store.loadSenderKey(group_sender)
        if senderKeyRecord.isEmpty():
            print("Decrypt Message - call process", message)
            self.my_session_builder.process(group_sender, received_sender_distribution_message)

        my_group_cipher = GroupCipher(self.my_sender_store, group_sender)
        message_plain_text = my_group_cipher.decrypt(message)
        # return encrypt message
        return message_plain_text
