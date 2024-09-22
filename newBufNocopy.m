/*
 * To compile objective-c on the command line:
 *
 * gcc -framework Foundation objc-gcc.m
 * clang -framework CoreGraphics -framework Foundation -framework Metal newbufnocopy.m -o newbufnocopy && ./newbufnocopy
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
     
        int input1[] = {10,20,30,40};

        NSMutableData *input1Data = [NSMutableData dataWithBytes:input1 length:4 * sizeof(int)];
        NSLog(@"NSMutable data created");
        id<MTLBuffer> buf1 = [device newBufferWithBytesNoCopy:input1Data
                                        length:[input1Data length]
                                        options:0
                                        deallocator:nil
                                        ];
        NSLog(@"Device buffer created");
        int *data = [buf1 contents];
        for (int i = 0; i < 4; i++) {
            printf("data[%d] = %d\n", i, data[i]);
        }
}