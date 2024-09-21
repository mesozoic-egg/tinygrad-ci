

import ctypes
from typing import cast
import numpy as np
import cdll

def main():
  device = cdll.metal.MTLCreateSystemDefaultDevice()
  commandQueue = cdll.send_message(device, "newCommandQueueWithMaxCommandBufferCount:", 1024)
  return

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
  # library_contents_ptr = cdll.send_message(library, "libraryDataContents")
  # library_contents_bytes_ptr = cdll.send_message(library_contents_ptr, "bytes")
  # library_length = cast(int, cdll.send_message(library_contents_ptr, "length", restype=ctypes.c_ulong))
  # library_bytes = ctypes.string_at(library_contents_bytes_ptr, library_length)
  kernelFunction = cdll.send_message(library, "newFunctionWithName:", cdll.to_ns_str("E_4n1"))

  buf_ptr_0 = (ctypes.c_char * 16)()
  buf_ptr_1 = (ctypes.c_char * 16)()
  buf_ptr_2 = (ctypes.c_char * 16)()

  buf_memoryview_0 = memoryview(buf_ptr_0).cast("B")
  buf_memoryview_1 = memoryview(buf_ptr_1).cast("B")
  buf_memoryview_2 = memoryview(buf_ptr_2).cast("B")
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

  icb_descriptor = cdll.send_message(cdll.libobjc.objc_getClass(b"MTLIndirectCommandBufferDescriptor"), "new")
  cdll.send_message(icb_descriptor, "setCommandTypes:", 32)
  cdll.send_message(icb_descriptor, "setInheritBuffers:", False)
  cdll.send_message(icb_descriptor, "setInheritPipelineState:", False)
  cdll.send_message(icb_descriptor, "setMaxKernelBufferBindCount:", 31)

  icb = cdll.send_message(device, "newIndirectCommandBufferWithDescriptor:maxCommandCount:options:", icb_descriptor, 1, 0)

  icbComputeCommand = cdll.send_message(icb, "indirectComputeCommandAtIndex:", 0)
  cdll.send_message(icbComputeCommand, "setComputePipelineState:", pipelineState)
  cdll.send_message(icbComputeCommand, "setKernelBuffer:offset:atIndex:", buf0, 0, 0)
  cdll.send_message(icbComputeCommand, "setKernelBuffer:offset:atIndex:", buf1, 0, 1)
  cdll.send_message(icbComputeCommand, "setKernelBuffer:offset:atIndex:", buf2, 0, 2)
  cdll.send_message(icbComputeCommand, "concurrentDispatchThreadgroups:threadsPerThreadgroup:", numThreadgroups, numthreads)
  cdll.send_message(icbComputeCommand, "setBarrier")

  cdll.send_message(encoder, "setBuffer:offset:atIndex:", buf0, 0, 0)
  cdll.send_message(encoder, "setBuffer:offset:atIndex:", buf1, 0, 1)
  cdll.send_message(encoder, "setBuffer:offset:atIndex:", buf2, 0, 2)
  cdll.send_message(encoder, "dispatchThreadgroups:threadsPerThreadgroup:", numThreadgroups, numthreads)
  cdll.send_message(encoder, "endEncoding")
  cdll.send_message(commandBuffer, "commit")
  cdll.send_message(commandBuffer, "waitUntilCompleted")


  print(np.frombuffer(buf_memoryview_0, dtype=np.int32))

  buf_memoryview_1[:] = np.array([11, 12, 13, 14], dtype=np.int32).data.cast("B")
  buf_memoryview_2[:] = np.array([11, 12, 13, 14], dtype=np.int32).data.cast("B")

  commandBuffer2 = cdll.send_message(commandQueue, "commandBuffer")
  encoder2 = cdll.send_message(commandBuffer2, "computeCommandEncoder")

  all_resources = [buf0, buf1, buf2]
  all_resources_ptr = cdll.to_ns_array(all_resources)
  cdll.send_message(encoder2, "useResources:count:usage:", all_resources_ptr, 3, 3)
  cdll.send_message(encoder2, "setComputePipelineState:", pipelineState)
  cdll.send_message(encoder2, "executeCommandsInBuffer:withRange:", icb, cdll.int_tuple_to_struct((0,1)))
  cdll.send_message(encoder2, "endEncoding")
  cdll.send_message(commandBuffer2, "commit")
  cdll.send_message(commandBuffer2, "waitUntilCompleted")

  print(np.frombuffer(buf_memoryview_0, dtype=np.int32))


main()