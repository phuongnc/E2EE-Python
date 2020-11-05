import client
import logging

def run():
        # init alice client
        alice = client.ClientTest('alice', '54321', 'localhost', 50051)
        alice.subscribe()
        alice.register_keys(1, 1)

        message = input("Start message to bob: \n")
        alice.publish(message, 'bob')
        while True: #just for keep terminal and get value from keyboard
            message = input("")
            alice.publish(message, 'bob')

if __name__ == '__main__':
    logging.basicConfig()
    run()