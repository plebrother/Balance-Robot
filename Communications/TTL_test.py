import time
from PC_Client import connect_to_server,send_message,receive_message

times = []
sock = connect_to_server()

loop = int(input("enter number of test:"))

for i in range(loop):
    t1 = time.time()
    send_message(sock,str(i))
    rec = receive_message(sock)
    t2 = time.time()
    print(rec)
    times.append(t2-t1)


average = 0
for i in times:
    average += i
average = average / loop

print("average dalay: {}".format(average))
print("max delay: {}".format(max(times)))
print("min delay: {}".format(min(times)))
