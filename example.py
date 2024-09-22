

import ctypes
from typing import cast
import numpy as np
import cdll

def main():
  device = cdll.metal.MTLCreateSystemDefaultDevice()
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

  numThreadgroups = cdll.int_tuple_to_struct((1,1,1))
  numthreads = cdll.int_tuple_to_struct((1,1,1))
  options = cdll.send_message(
              cdll.libobjc.objc_getClass(b"MTLCompileOptions"),
              "new",
          )
  cdll.send_message(options, "setFastMathEnabled:", False)
  library = cdll.send_message(device, "newLibraryWithSource:options:error:", cdll.to_ns_str(src), options, None)

  kernelFunction = cdll.send_message(library, "newFunctionWithName:", cdll.to_ns_str("E_4n1"))

  buf_ptr_0 = (ctypes.c_char * 16)()
  buf_ptr_1 = (ctypes.c_char * 16)()
  buf_ptr_2 = (ctypes.c_char * 16)()

  buf_memoryview_0 = memoryview(buf_ptr_0).cast("B")
  buf_memoryview_1 = memoryview(buf_ptr_1).cast("B")
  buf_memoryview_2 = memoryview(buf_ptr_2).cast("B")

  buf0_ns_data = cdll.send_message(
    cdll.libobjc.objc_getClass(b"NSMutableData"),
    "dataWithBytes:length:",
    buf_ptr_0,
    4*4
  )
  print("buf0_ns_data", buf0_ns_data, buf0_ns_data.value)

  buf0 = cdll.send_message(device, "newBufferWithBytesNoCopy:length:options:deallocator:", buf_ptr_0, 4*4, 0, None)
  buf1 = cdll.send_message(device, "newBufferWithBytesNoCopy:length:options:deallocator:", buf_ptr_1, 4*4, 0, None)
  buf2 = cdll.send_message(device, "newBufferWithBytesNoCopy:length:options:deallocator:", buf_ptr_2, 4*4, 0, None)

  buf_memoryview_1[:] = np.array([1,2,3,4], dtype=np.int32).data.cast("B")
  buf_memoryview_2[:] = np.array([1,2,3,4], dtype=np.int32).data.cast("B")
  commandBuffer = cdll.send_message(commandQueue, "commandBuffer")
  encoder = cdll.send_message(commandBuffer, "computeCommandEncoder")

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

  print(np.frombuffer(buf_memoryview_1, dtype=np.int32))
  print(np.frombuffer(buf_memoryview_2, dtype=np.int32))
  print(np.frombuffer(buf_memoryview_0, dtype=np.int32))


main()