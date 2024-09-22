from tinygrad.codegen.kernel import Opt, OptOps
from tinygrad.codegen.kernel import Kernel
from tinygrad.ops import UOp, UOps, BinaryOps
from tinygrad.engine.schedule import create_schedule
from tinygrad.engine.search import time_linearizer, bufs_from_lin, actions, beam_search
from tinygrad.device import Device, Buffer
from tinygrad.tensor import Tensor
from tinygrad.dtype import dtypes, PtrDType
from tinygrad.helpers import Context, GlobalCounters
from tinygrad.engine.realize import capturing
from tinygrad.shape.shapetracker import ShapeTracker
from tinygrad.shape.view import View

si = [i for i in create_schedule([Tensor([1,2,3,4]).add(1).lazydata]) if i.ast.op is UOps.SINK][0]
out = Buffer(Device.DEFAULT, si.outputs[0].size, si.outputs[0].dtype).allocate()
memops = {x.src[0].arg:x.src[-1].arg.real_size() for x in si.ast.parents if x.op is UOps.LOAD}
rawbufs = [out] + [Buffer(Device.DEFAULT, memops[i], x.dtype).allocate() for i,x in enumerate(si.inputs, start=len(si.outputs))]
tm = time_linearizer(Kernel(si.ast), rawbufs, allow_test_size=False, cnt=10, disable_cache=True)
print(f"{tm=}")