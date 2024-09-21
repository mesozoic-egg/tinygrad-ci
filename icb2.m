/*
 * To compile objective-c on the command line:
 *
 * gcc -framework Foundation objc-gcc.m
 * clang -framework CoreGraphics -framework Foundation -framework Metal icb2.m -o icb2 && ./icb2
 *
 * You may have to link with -lobjc or other libs,
 * as required.
 */

#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <CoreGraphics/CoreGraphics.h>

int main(int argc, char** argv)
{
        id<MTLDevice> device = MTLCreateSystemDefaultDevice();
        id<MTLCommandQueue> commandQueue = [device newCommandQueue];
        NSError* compileError;
        MTLCompileOptions* compileOptions = [MTLCompileOptions new];
        id<MTLLibrary> library = [device newLibraryWithSource:
@"#include <metal_stdlib>\n"
"using namespace metal;\n"
"kernel void E_4n1(device int* data0, const device int* data1, const device int* data2, uint3 gid [[threadgroup_position_in_grid]], uint3 lid [[thread_position_in_threadgroup]]) {\n"
"  int val0 = *(data1+0);\n"
"  int val1 = *(data1+1);\n"
"  int val2 = *(data1+2);\n"
"  int val3 = *(data1+3);\n"
"  int val4 = *(data2+0);\n"
"  int val5 = *(data2+1);\n"
"  int val6 = *(data2+2);\n"
"  int val7 = *(data2+3);\n"
"  *(data0+0) = (val0+val4);\n"
"  *(data0+1) = (val1+val5);\n"
"  *(data0+2) = (val2+val6);\n"
"  *(data0+3) = (val3+val7);\n"
"}\n"
         options: compileOptions error: nil];
        id<MTLFunction> kernelFunction = [library newFunctionWithName:@"E_4n1"];
        //----------------------------------------------------------------------
        // pipeline
        NSError *error = NULL;
        int input1[] = {10,20,30,40};
        int input2[] = {10,20,30,40};
        NSInteger dataSize = sizeof(input1);
        MTLSize numThreadgroups = {1,1,1};
        MTLSize numgroups = {1,1,1};
        
        id<MTLBuffer> buf1 = [device newBufferWithLength:4*sizeof(int) options:1];

        id<MTLBuffer> buf2 = [device newBufferWithLength:4*sizeof(int) options:1];

        int *input1_contents = [buf1 contents];
        int *input2_contents = [buf2 contents];
        for (int i = 0; i < 4; i++) {
            input1_contents[i] = input1[i];
            input2_contents[i] = input2[i];
        }

        id<MTLBuffer> outputBuffer = [device newBufferWithLength:4*sizeof(int) options:1];

        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];


        MTLComputePipelineDescriptor *pipelineDescriptor = [[MTLComputePipelineDescriptor alloc] init];
        pipelineDescriptor.computeFunction = kernelFunction;
        pipelineDescriptor.supportIndirectCommandBuffers = TRUE;

        id<MTLComputePipelineState> pipelineState = [device newComputePipelineStateWithDescriptor:pipelineDescriptor 
            options:0 reflection:nil error:&error];
        if (!pipelineState) {
            NSLog(@"Failed to create pipeline state: %@", error);
            return 1;
        }
        [encoder setComputePipelineState:pipelineState];

        MTLIndirectCommandBufferDescriptor* icb_descriptor = [MTLIndirectCommandBufferDescriptor new];
        icb_descriptor.commandTypes = MTLIndirectCommandTypeConcurrentDispatch;
        icb_descriptor.inheritBuffers = NO;
        icb_descriptor.inheritPipelineState = FALSE;
        icb_descriptor.maxKernelBufferBindCount = 31;
        id<MTLIndirectCommandBuffer> icb = [device newIndirectCommandBufferWithDescriptor:icb_descriptor maxCommandCount:1 options:0];
        MTLIndirectCommandBufferExecutionRange range = MTLIndirectCommandBufferExecutionRangeMake(0, 1);
        id<MTLIndirectComputeCommand> icbComputeCommand2 = [icb indirectComputeCommandAtIndex:0];
        [icbComputeCommand2 setComputePipelineState:pipelineState];
        [icbComputeCommand2 setKernelBuffer:outputBuffer offset:0 atIndex:0];
        [icbComputeCommand2 setKernelBuffer: buf1 offset:0 atIndex:1];
        [icbComputeCommand2 setKernelBuffer:buf2 offset:0 atIndex:2];
        [icbComputeCommand2 concurrentDispatchThreadgroups:numThreadgroups threadsPerThreadgroup:numgroups];
        [icbComputeCommand2 setBarrier];
        //----------------------------------------------------------------------
        // Set Data

        [encoder setBuffer:outputBuffer offset:0 atIndex:0];
        [encoder setBuffer:buf1 offset:0 atIndex:1];
        [encoder setBuffer:buf2 offset:0 atIndex:2];
        //----------------------------------------------------------------------
        // Run Kernel

        [encoder dispatchThreadgroups:numThreadgroups threadsPerThreadgroup:numgroups];
        [encoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];
        //----------------------------------------------------------------------
        // Results
        int *output = [outputBuffer contents];
        for (int i = 0; i < 4; i++) {
            printf("output[%d] = %d\n", i, output[i]);
        }

        int input3[] = {1,2,3,4};
        int input4[] = {1,2,3,4};
        
        int *input3_contents = [buf1 contents];
        int *input4_contents = [buf2 contents];
        for (int i = 0; i < 4; i++) {
            input3_contents[i] = input3[i];
            input4_contents[i] = input4[i];
        }
        id<MTLCommandBuffer> commandBuffer2 = [commandQueue commandBuffer];
        id<MTLComputeCommandEncoder> encoder2 = [commandBuffer2 computeCommandEncoder];

        id<MTLBuffer> allResources[3] = {outputBuffer, buf1, buf2};

        [encoder2 useResources:allResources count:3 usage:MTLResourceUsageRead|MTLResourceUsageWrite];

        [encoder2 setComputePipelineState:pipelineState];
        MTLSize numThreadgroups2 = {0,0,0};
        MTLSize numgroups2 = {0,0,0};
        [encoder2 dispatchThreadgroups:numThreadgroups2 threadsPerThreadgroup:numgroups2];


        [encoder2 executeCommandsInBuffer:icb withRange:NSMakeRange(0, 1)];
        [encoder2 endEncoding];
        [commandBuffer2 commit];
        [commandBuffer2 waitUntilCompleted];
        int *output2_contents = [outputBuffer contents];
        for (int i = 0; i < 4; i++) {
            printf("output2[%d] = %d\n", i, output2_contents[i]);
        }


}