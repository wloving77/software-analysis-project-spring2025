#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ===-- ktest-tool --------------------------------------------------------===##
# 
#                      The KLEE Symbolic Virtual Machine
# 
#  This file is distributed under the University of Illinois Open Source
#  License. See LICENSE.TXT for details.
# 
# ===----------------------------------------------------------------------===##

import binascii
import io
import string
import struct
import sys

version_no = 3


class KTestError(Exception):
    pass


class KTest:
    valid_chars = string.digits + string.ascii_letters + string.punctuation + ' '

    @staticmethod
    def fromfile(path):
        try:
            f = open(path, 'rb')
        except IOError:
            print('ERROR: file %s not found' % path)
            sys.exit(1)

        hdr = f.read(5)
        if len(hdr) != 5 or (hdr != b'KTEST' and hdr != b'BOUT\n'):
            raise KTestError('unrecognized file')
        version, = struct.unpack('>i', f.read(4))
        if version > version_no:
            raise KTestError('unrecognized version')
        numArgs, = struct.unpack('>i', f.read(4))
        args = []
        for i in range(numArgs):
            size, = struct.unpack('>i', f.read(4))
            args.append(str(f.read(size).decode(encoding='ascii')))

        if version >= 2:
            symArgvs, = struct.unpack('>i', f.read(4))
            symArgvLen, = struct.unpack('>i', f.read(4))
        else:
            symArgvs = 0
            symArgvLen = 0

        numObjects, = struct.unpack('>i', f.read(4))
        objects = []
        for i in range(numObjects):
            size, = struct.unpack('>i', f.read(4))
            name = f.read(size).decode('utf-8')
            size, = struct.unpack('>i', f.read(4))
            bytes = f.read(size)
            objects.append((name, bytes))

        # Create an instance
        b = KTest(version, path, args, symArgvs, symArgvLen, objects)
        return b

    def __init__(self, version, path, args, symArgvs, symArgvLen, objects):
        self.version = version
        self.path = path
        self.symArgvs = symArgvs
        self.symArgvLen = symArgvLen
        self.args = args
        self.objects = objects

    def __format__(self, format_spec):
        sio = io.StringIO()
        width = str(len(str(max(1, len(self.objects) - 1))))

        # print ktest info
        print('ktest file : %r' % self.path, file=sio)
        print('args       : %r' % self.args, file=sio)
        print('num objects: %r' % len(self.objects), file=sio)

        # format strings
        fmt = dict()
        fmt['name'] = "object {0:" + width + "d}: name: '{1}'"
        fmt['size'] = "object {0:" + width + "d}: size: {1}"
        fmt['int' ] = "object {0:" + width + "d}: int : {1}"
        fmt['uint'] = "object {0:" + width + "d}: uint: {1}"
        fmt['data'] = "object {0:" + width + "d}: data: {1}"
        fmt['hex' ] = "object {0:" + width + "d}: hex : 0x{1}"
        fmt['text'] = "object {0:" + width + "d}: text: {1}"

        # print objects
        for i, (name, data) in enumerate(self.objects):
            def p(key, arg): print(fmt[key].format(i, arg), file=sio)

            blob = data.rstrip(b'\x00') if format_spec.endswith('trimzeros') else data
            txt = ''.join(c if c in self.valid_chars else '.' for c in blob.decode('ascii', errors='replace').replace('�', '.'))
            size = len(data)

            p('name', name)
            p('size', size)
            p('data', blob)
            p('hex', binascii.hexlify(blob).decode('ascii'))
            for n, m in [(1, 'b'), (2, 'h'), (4, 'i'), (8, 'q')]:
                if size == n:
                    p('int', struct.unpack(m, data)[0])
                    p('uint', struct.unpack(m.upper(), data)[0])
                    break
            p('text', txt)

        return sio.getvalue()

    def extract(self, object_names, trim_zeros):
        extracted_objects = set()
        for name, data in self.objects:
            if name not in object_names:
                continue

            f = open(self.path + '.' + name, 'wb')
            blob = data.rstrip(b'\x00') if trim_zeros else data
            f.write(blob)
            f.close()
            extracted_objects.add(name)
        missing_objects = list(object_names - extracted_objects)
        missing_objects.sort()
        if missing_objects:
            sys.exit(f'Could not find object{"s"[:len(missing_objects)^1]}: {", ".join(missing_objects)}')




def main():
    epilog = """
        output description:
          A .ktest file comprises a file header and a list of memory objects.
          Each object holds concrete test data for a symbolic memory object.
          As no type information is stored, ktest-tool outputs data in
          different representations.

          ktest file header:
            ktest file: path to ktest file
            args: program arguments
            num objects: number of memory objects
          memory object:
            name: object name
            size: object size
            data: concrete object data as Python byte string
            hex: data as hex string
            int: data as integer if size is 1, 2, 4, 8 bytes
            uint: data as unsigned integer if size is 1, 2, 4, 8 bytes
            text: data as ascii text, '.' for non-printable characters

        example:
          > ktest-tool klee-last/test000003.ktest
          ktest file : 'klee-last/test000003.ktest'
          args       : ['get_sign.bc']
          num objects: 1
          object 0: name: 'a'
          object 0: size: 4
          object 0: data: b'\\x00\\x00\\x00\\x80'
          object 0: hex : 0x00000080
          object 0: int : -2147483648
          object 0: uint: 2147483648
          object 0: text: ....
    """

    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    from textwrap import dedent

    ap = ArgumentParser(prog='ktest-tool', formatter_class=RawDescriptionHelpFormatter, epilog=dedent(epilog))
    ap.add_argument('--trim-zeros', help='trim trailing zeros', action='store_true')
    ap.add_argument('--extract', help='write binary value of object into file', metavar='name', nargs=1, action='append')
    ap.add_argument('files', help='a .ktest file', metavar='file', nargs='+')
    args = ap.parse_args()

    for file in args.files:
        ktest = KTest.fromfile(file)
        if args.extract:
            ktest.extract({x for xs in args.extract for x in xs}, args.trim_zeros)
        else:
            fmt = '{:trimzeros}' if args.trim_zeros else '{}'
            print(fmt.format(ktest), end='')


if __name__ == '__main__':
    main()