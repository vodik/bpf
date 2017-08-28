# cython: language_level=3
from cython cimport Py_buffer, Py_ssize_t
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cython.operator cimport dereference as deref, preincrement as inc
from libc.stdint cimport uint8_t, uint32_t, uintptr_t
from libc.string cimport memcpy, memset
from libcpp.unordered_map cimport unordered_map
from libcpp.string cimport string


cdef object unpack_uint32(uint8_t *data):
    cdef uint32_t value
    memcpy(&value, data, sizeof(value))
    return value


cdef object pack_uint32(uint8_t *data, object obj):
    cdef uint32_t value = obj
    memcpy(data, &value, sizeof(value))


cdef struct formatdef:
    Py_ssize_t offset
    object (*pack)(uint8_t *, object)
    object (*unpack)(uint8_t *)


ctypedef unordered_map[string, formatdef] formatmap


cdef class View:
    cdef Struct struct
    cdef uint8_t *buf
    cdef Py_ssize_t shape[1]
    cdef Py_ssize_t strides[1]

    def __cinit__(self, Struct struct):
        self.struct = struct
        self.shape[0] = len(struct)
        self.strides[0] = 1

        self.buf = <uint8_t *>PyMem_Malloc(self.shape[0])
        if not self.buf:
            raise MemoryError()

        memset(self.buf, 0, self.shape[0])

    def __cdel__(self):
        PyMem_Free(self.buf)

    def keys(self):
        yield from self.struct.keys()

    def __getitem__(self, key):
        formatdef = self.struct.definition(key.encode())
        return formatdef.unpack(&self.buf[formatdef.offset])

    def __setitem__(self, key, value):
        formatdef = self.struct.definition(key.encode())
        formatdef.pack(&self.buf[formatdef.offset], value)

    def __len__(self):
        return self.shape[0]

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        buffer.buf = self.buf
        buffer.format = 'B'
        buffer.internal = NULL
        buffer.itemsize = 1
        buffer.len = self.shape[0]
        buffer.ndim = len(self.shape)
        buffer.obj = self
        buffer.readonly = 0
        buffer.shape = self.shape
        buffer.strides = self.strides
        buffer.suboffsets = NULL

    def __releasebuffer__(self, Py_buffer *buffer):
        pass


cdef class Struct:
    cdef str name
    cdef formatmap offsets

    def __cinit__(self, name):
        self.name = name
        self.offsets[b'foo'] = formatdef(
            offset=0,
            pack=pack_uint32,
            unpack=unpack_uint32
        )

        self.offsets[b'bar'] = formatdef(
            offset=sizeof(uint32_t),
            pack=pack_uint32,
            unpack=unpack_uint32
        )

        self.offsets[b'baz'] = formatdef(
            offset=sizeof(uint32_t) * 2,
            pack=pack_uint32,
            unpack=unpack_uint32
        )

    def __len__(self):
        return sizeof(uint32_t) * 3

    cdef formatdef definition(self, key):
        return self.offsets[key]

    def keys(self):
        it = self.offsets.begin()
        while it != self.offsets.end():
            yield deref(it).first.decode()
            inc(it)

    def parse(self, data):
        pass

    def create(self, **fields):
        view = View.__new__(View, self)
        for key, value in fields.items():
            view[key] = value
        return view


Header = Struct('Header')


def main():
    hdr = Header.create(
        foo=0x61,
        bar=0x62,
        baz=0x63
    )

    # print(bytes(hdr))
    # print(dict(hdr))

    memoryview(hdr)
    # print(bytes(hdr))
    # print(dict(hdr))


if __name__ == '__main__':
    main()
