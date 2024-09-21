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
        "kernel void add(const device float2 *in [[ buffer(0) ]],\n"
        "                device float  *out [[ buffer(1) ]],\n"
        "                uint id [[ thread_position_in_grid ]]) {\n"
        "out[id] = in[id].x + in[id].y;\n"
        "}\n"
         options: compileOptions error: nil];
        id<MTLFunction> kernelFunction = [library newFunctionWithName:@"add"];
        //----------------------------------------------------------------------
        // pipeline
        NSError *error = NULL;
        [commandQueue commandBuffer];
        id<MTLCommandBuffer> commandBuffer = [commandQueue commandBuffer];
        id<MTLComputeCommandEncoder> encoder = [commandBuffer computeCommandEncoder];
        [encoder setComputePipelineState:[device newComputePipelineStateWithFunction:kernelFunction error:&error]];
        //----------------------------------------------------------------------
        // Set Data
        float input[] = {1,2};
        NSInteger dataSize = sizeof(input);
        
        [encoder setBuffer:[device newBufferWithBytes:input length:dataSize options:0]
                    offset:0
                   atIndex:0];
        
        id<MTLBuffer> outputBuffer = [device newBufferWithLength:sizeof(float) options:0];
        [encoder setBuffer:outputBuffer offset:0 atIndex:1];
        //----------------------------------------------------------------------
        // Run Kernel
        MTLSize numThreadgroups = {1,1,1};
        MTLSize numgroups = {1,1,1};
        [encoder dispatchThreadgroups:numThreadgroups threadsPerThreadgroup:numgroups];
        [encoder endEncoding];
        [commandBuffer commit];
        [commandBuffer waitUntilCompleted];
        //----------------------------------------------------------------------
        // Results
        float *output = [outputBuffer contents];
        printf("result = %f\n", output[0]);
}