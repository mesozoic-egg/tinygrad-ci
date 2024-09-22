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
    int *buffer = malloc(4 * sizeof(int));
    buffer[0] = 10;
    buffer[1] = 20;
    buffer[2] = 30;
    buffer[3] = 40;
    for (int i = 0; i < 4; i++) {
        printf("Malloc data[%d] = %d\n", i, buffer[i]);
    }

    NSMutableData *ns_mutable = [NSMutableData dataWithBytesNoCopy:buffer length:4 * sizeof(int)];
    int length = [ns_mutable length];
    int* ns_mutable_ptr = [ns_mutable mutableBytes];
    printf("NSMutable data created\n");
    printf("Length: %d\n", length);
    for (int i = 0; i < 4; i++) {
        printf("NSMutable data[%d] = %d\n", i, ns_mutable_ptr[i]);
    }

    id<MTLBuffer> device_buffer = [device newBufferWithBytesNoCopy:ns_mutable_ptr
                                                            length:length
                                                           options:0
                                                       deallocator:nil
    ];
    printf("Device buffer created\n");
    int length2 = [device_buffer length];
    printf("Length: %d\n", length2);
    int *data = [device_buffer contents];
    printf("Data pointer obtained\n");
    for (int i = 0; i < 4; i++) {
        printf("Device buffer[%d] = %d\n", i, data[i]);
    }
}