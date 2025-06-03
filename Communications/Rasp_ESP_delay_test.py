import time
from Raspberry_To_ESP32 import send_command,read_response

times = []


for i in range(100):
    t1 = time.time()
    send_command(str(i))
    rec = read_response()
    t2 = time.time()
    print(rec)
    times.append(t2-t1)

average = 0
for i in times:
    average += i
average = average / 100

print("average dalay: {}".format(average))
print("max delay: {}".format(max(times)))
print("min delay: {}".format(min(times)))
