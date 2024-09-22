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
     
        int *input1 = malloc(4 * sizeof(int));
        input1[0] = 10;
        input1[1] = 20;
        input1[2] = 30;
        input1[3] = 40;
        NSMutableData *input1Data = [NSMutableData dataWithBytesNoCopy:input1 length:4 * sizeof(int)];
        int length = [input1Data length];
        NSLog(@"NSMutable data created");
        NSLog(@"Length: %d", length);
        id<MTLBuffer> buf1 = [device newBufferWithBytesNoCopy:input1Data
                                        length:length
                                        options:0
                                        deallocator:nil
                                        ];
        NSLog(@"Device buffer created");
        int length2 = [buf1 length];
        NSLog(@"Length: %d", length2);
        int *data = [buf1 contents];
        NSLog(@"Data pointer obtained");
        for (int i = 0; i < 4; i++) {
            printf("data input1[%d] = %d\n", i, input1[i]);
            printf("data[%d] = %d\n", i, data[i]);
        }
}