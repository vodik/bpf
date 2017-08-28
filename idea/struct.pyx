# cython: language_level=3
from cython cimport Py_buffer, Py_ssize_t
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
    cdef uint8_t[:] buf
    cdef Py_ssize_t shape[1]
    cdef Py_ssize_t strides[1]

    def __cinit__(self, Struct struct, uint8_t[:] buf):
        self.struct = struct
        self.buf = buf
        self.shape[0] = len(struct)
        self.strides[0] = 1

    def keys(self):
        yield from self.struct.keys()

    def __getitem__(self, key):
        try:
            formatdef = self.struct.definition(key.encode())
            return formatdef.unpack(&self.buf[formatdef.offset])
        except IndexError:
            raise AttributeError(key) from None

    def __setitem__(self, key, value):
        try:
            formatdef = self.struct.definition(key.encode())
            formatdef.pack(&self.buf[formatdef.offset], value)
        except IndexError:
            raise AttributeError(key) from None

    def __len__(self):
        return self.shape[0]

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        buffer.buf = &self.buf[0]
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
    cdef Py_ssize_t length
    cdef formatmap offsets
    cdef str name

    def __cinit__(self, name, *fields):
        cdef Py_ssize_t offset = 0
        for name, field in fields:
            assert field == 'uint32'

            self.offsets[name.encode()] = formatdef(
                offset=offset,
                pack=pack_uint32,
                unpack=unpack_uint32
            )
            offset += sizeof(uint32_t)

        self.length = offset
        self.name = name

    def __len__(self):
        return self.length

    cdef formatdef definition(self, key) except + :
        return self.offsets.at(key)

    def keys(self):
        it = self.offsets.begin()
        while it != self.offsets.end():
            yield deref(it).first.decode()
            inc(it)

    def parse(self, data not None):
        return View.__new__(View, self, data)

    def create(self, **fields):
        data = bytearray(len(self))
        view = View.__new__(View, self, data)
        for key, value in fields.items():
            view[key] = value
        return view

    def __call__(self, **fields):
        return self.create(**fields)

    def __repr__(self):
        return f'<Struct {self.name} len={len(self)}>'


Header = Struct('Header',
    ('foo', 'uint32'),
    ('bar', 'uint32'),
    ('baz', 'uint32'),
)


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
