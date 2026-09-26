import io, os, gc, weakref, zipfile, pathlib
real_FileIO = io.FileIO
tracked = {}

class Meta(type(real_FileIO)):
    def __instancecheck__(cls, o): return isinstance(o, real_FileIO)
    def __subclasscheck__(cls, c): return issubclass(c, real_FileIO)

class VFileIO(real_FileIO, metaclass=Meta):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        if k.get("closefd", True) and (len(a) < 3 or a[2]):
            try: tracked[self.fileno()] = weakref.ref(self)
            except Exception: pass

def vopen_code(p): return VFileIO(p, "rb")

io.FileIO = VFileIO
io.open_code = vopen_code
try:
    f = io.FileIO(P); print("direct FileIO tracked:", f.fileno() in tracked, "isinstance real:", isinstance(f, real_FileIO), "isinstance io.FileIO:", isinstance(f, io.FileIO)); f.close()
    raw = real_open := None
except Exception as e:
    print("ERR1", type(e).__name__, e)
raw = builtins.open(P, "rb", buffering=0)
print("real raw isinstance io.FileIO (metaclass fwd):", isinstance(raw, io.FileIO)); raw.close()
h = io.open_code(P); print("open_code tracked:", h.fileno() in tracked); h.close()
# borrowed fd not tracked
fd = os.open(P, os.O_RDONLY)
g = io.FileIO(fd, "rb", False)
print("borrowed tracked:", g.fileno() in tracked)
g.close(); os.close(fd)
# libraries still fine
print("zipfile ok:", zipfile.ZipFile(Z).namelist(), "pathlib ok:", len(pathlib.Path(P).read_text()))
print("import still works:", __import__("csv").__name__)
# leak check on direct FileIO now trackable
base = len(os.listdir("/dev/fd"))
for _ in range(25): io.FileIO(P)
gc.collect()
dead = sum(1 for fd_, r in list(tracked.items()) if r() is None)
print("after 25 dropped FileIO: registry", len(tracked), "dead refs:", dead, "fd delta", len(os.listdir("/dev/fd"))-base)
closed = 0
for fd_, r in list(tracked.items()):
    if r() is None:
        try: os.close(fd_); closed += 1
        except Exception: pass
        tracked.pop(fd_, None)
print("reclaimed:", closed, "fd delta after reclaim:", len(os.listdir("/dev/fd"))-base)
io.FileIO = real_FileIO
