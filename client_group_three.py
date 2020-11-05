import client_group
import logging

def run():
        # init two client
        three = client_group.ClientGroupTest('three', 3, '172.16.0.216', 50052)
        three.subscribe()
        three.register_group_keys("test-group")
        message = input("Start message to group: \n")
        three.publish(message, "test-group")
        while True: #just for keep terminal and get value from keyboard
            message = input("")
            three.publish(message, "test-group")

if __name__ == '__main__':
    logging.basicConfig()
    run()