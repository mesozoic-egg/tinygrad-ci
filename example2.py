import cdll
import ctypes
import numpy as np



def main():
    device = cdll.metal.MTLCreateSystemDefaultDevice()

    def create_buffer(data):
      buffer = cdll.send_message(device, "newBufferWithLength:options:", 16, 0)
      ptr = cdll.send_message(buffer, "contents")
      array = (ctypes.c_char * 16).from_address(ptr.value)
      mem = memoryview(array).cast("B")
    
      mem[:] = data[:]
      return buffer
    
    def as_buffer(src, size):
       ptr = cdll.send_message(src, "contents")
       array = (ctypes.c_char * size).from_address(ptr.value)
       mem = memoryview(array).cast("B")
       return mem
    
    np_data1 = np.array([1,2,3,4], dtype=np.int32).data.cast("B")
    np_data2 = np.array([5,6,7,8], dtype=np.int32).data.cast("B")
    buf0 = cdll.send_message(device, "newBufferWithLength:options:", 16, 0)
    buf1 = create_buffer(np_data1)
    buf2 = create_buffer(np_data2)

    commandQueue = cdll.send_message(device, "newCommandQueueWithMaxCommandBufferCount:", 1024)
    src = """
    #include <metal_stdlib>
    using namespace metal;
    kernel void E_4n1(device int* data0, const device int* data1, const device int* data2, uint3 gid [[threadgroup_position_in_grid]], uint3 lid [[thread_position_in_threadgroup]]) {
        int val0 = *(data1+0);
        int val1 = *(data1+1);
        int val2 = *(data1+2);
        int val3 = *(data1+3);
        int val4 = *(data2+0);
        int val5 = *(data2+1);
        int val6 = *(data2+2);
        int val7 = *(data2+3);
        *(data0+0) = (val0+val4);
        *(data0+1) = (val1+val5);
        *(data0+2) = (val2+val6);
        *(data0+3) = (val3+val7);
    }
    """
    commandBuffer = cdll.send_message(commandQueue, "commandBuffer")
    encoder = cdll.send_message(commandBuffer, "computeCommandEncoder")

    numThreadgroups = cdll.int_tuple_to_struct((1,1,1))
    numthreads = cdll.int_tuple_to_struct((1,1,1))
    options = cdll.send_message(
                cdll.libobjc.objc_getClass(b"MTLCompileOptions"),
                "new",
            )
    cdll.send_message(options, "setFastMathEnabled:", False)
    library = cdll.send_message(device, "newLibraryWithSource:options:error:", cdll.to_ns_str(src), options, None)

    kernelFunction = cdll.send_message(library, "newFunctionWithName:", cdll.to_ns_str("E_4n1"))
    pipelineDescriptor = cdll.send_message(cdll.libobjc.objc_getClass(b"MTLComputePipelineDescriptor"), "new")
    cdll.send_message(pipelineDescriptor, "setComputeFunction:", kernelFunction)
    cdll.send_message(pipelineDescriptor, "setSupportIndirectCommandBuffers:", True)

    pipelineState = cdll.send_message(device, "newComputePipelineStateWithDescriptor:options:reflection:error:", pipelineDescriptor, 0, None, None)
    cdll.send_message(encoder, "setComputePipelineState:", pipelineState)
    cdll.send_message(encoder, "setBuffer:offset:atIndex:", buf0, 0, 0)
    cdll.send_message(encoder, "setBuffer:offset:atIndex:", buf1, 0, 1)
    cdll.send_message(encoder, "setBuffer:offset:atIndex:", buf2, 0, 2)
    cdll.send_message(encoder, "dispatchThreadgroups:threadsPerThreadgroup:", numThreadgroups, numthreads)
    cdll.send_message(encoder, "endEncoding")
    cdll.send_message(commandBuffer, "commit")
    cdll.send_message(commandBuffer, "waitUntilCompleted")
    print(np.frombuffer(as_buffer(buf0, 16), dtype=np.int32))
    start_time = cdll.send_message(commandBuffer, "GPUStartTime", restype=ctypes.c_double)
    end_time = cdll.send_message(commandBuffer, "GPUEndTime", restype=ctypes.c_double)
    elapsed = end_time - start_time
    print(f"Start: {start_time}, End: {end_time}, Elapsed: {elapsed}")


if __name__ == "__main__":
    main()
