import cdll
import ctypes
import numpy as np
def main1():
    device = cdll.metal.MTLCreateSystemDefaultDevice()
    buffer = cdll.send_message(device, "newBufferWithLength:options:", 16, 0)
    contents_address: int = cdll.send_message(buffer, "contents", restype=ctypes.POINTER(ctypes.c_int))
    ptr = contents_address
    print(ptr[0])
    ptr[0] = ctypes.c_int(10)
    print(ptr[0])
    contents_address2 = cdll.send_message(buffer, "contents", restype=ctypes.POINTER(ctypes.c_int))
    print(contents_address2[0])

def main2():
    device = cdll.metal.MTLCreateSystemDefaultDevice()
    buffer = cdll.send_message(device, "newBufferWithLength:options:", 16, 0)
    ptr = cdll.send_message(buffer, "contents")
    array = (ctypes.c_int * 4).from_address(ptr.value)
    mem = memoryview(array).cast("B")
    for i in range(4):
        print('element at', i, ':', array[i])
    np_data = np.array([1,2,3,4], dtype=np.int32).data.cast("B")
    mem[:] = np_data[:]
    for i in range(4):
        print('element at', i, ':', array[i])

def main3():
    device = cdll.metal.MTLCreateSystemDefaultDevice()
    buffer = cdll.send_message(device, "newBufferWithLength:options:", 16, 0)
    ptr = cdll.send_message(buffer, "contents")
    array = (ctypes.c_char * 16).from_address(ptr.value)
    mem = memoryview(array).cast("B")
    for i in range(4):
        print('element at', i, ':', array[i])
    np_data = np.array([1,2,3,4], dtype=np.int32).data.cast("B")
    mem = mem[0:]
    print(mem.nbytes)
    mem[:] = np_data[:]
    for i in range(4):
        print('element at', i, ':', array[i])
    print(np.frombuffer(mem, dtype=np.int32))

if __name__ == "__main__":
    main3()
