/*
 * To compile objective-c on the command line:
 *
 * gcc -framework Foundation objc-gcc.m
 * clang -framework CoreGraphics -framework Foundation -framework Metal example1.m -o example1 && ./example1
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
        
        // id<MTLBuffer> buf1 = [device newBufferWithLength:4*sizeof(int) options:1];
        NSMutableData *input1Data = [NSMutableData dataWithBytes:input1 length:4 * sizeof(int)];
        id<MTLBuffer> buf1 = [device newBufferWithBytesNoCopy:input1Data
                                        length:[input1Data length]
                                        options:0
                                        deallocator:nil
                                        ];
        NSMutableData *input2Data = [NSMutableData dataWithBytes:input2 length:4 * sizeof(int)];
        id<MTLBuffer> buf2 = [device newBufferWithBytesNoCopy:input2Data
                                        length:[input2Data length]
                                        options:0
                                        deallocator:nil
                                        ];

        NSMutableData *outputData = [NSMutableData dataWithLength:4*sizeof(int)];
        id<MTLBuffer> outputBuffer = [device newBufferWithBytesNoCopy:outputData
                                        length:[outputData length]
                                        options:0
                                        deallocator:nil
                                        ];

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
        double start_time = [commandBuffer GPUStartTime];
        double end_time = [commandBuffer GPUEndTime];
        double elapsed = end_time - start_time;
        printf("Start: %f, End: %f, Elapsed: %f\n", start_time, end_time, elapsed);
}