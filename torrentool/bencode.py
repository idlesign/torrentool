from collections import OrderedDict
from operator import itemgetter
from codecs import encode
from sys import version_info

from .exceptions import BencodeDecodingError, BencodeEncodingError


PY3 = version_info >= (3, 0)

if PY3:
    str_type = str
    byte_types = (bytes, bytearray)
    chr_ = chr
    int_types = int
else:
    str_type = basestring
    byte_types = bytes
    chr_ = lambda ch: ch
    int_types = (int, long)


class Bencode(object):
    """Exposes utilities for bencoding."""

    @classmethod
    def encode(cls, value):
        """Encodes a value into bencoded bytes.

        :param value: Python object to be encoded (str, int, list, dict).
        :param str val_encoding: Encoding used by strings in a given object.
        :rtype: bytes
        """
        val_encoding = 'utf-8'

        def encode_str(v):
            try:
                v_enc = encode(v, val_encoding)

            except UnicodeDecodeError:
                if PY3:
                    raise
                else:
                    # Suppose bytestring
                    v_enc = v

            prefix = encode('%s:' % len(v_enc), val_encoding)
            return prefix + v_enc

        def encode_(val):
            if isinstance(val, str_type):
                result = encode_str(val)

            elif isinstance(val, int_types):
                result = encode(('i%se' % val), val_encoding)

            elif isinstance(val, (list, set, tuple)):
                result = encode('l', val_encoding)
                for item in val:
                    result += encode_(item)
                result += encode('e', val_encoding)

            elif isinstance(val, dict):
                result = encode('d', val_encoding)

                # Dictionaries are expected to be sorted by key.
                for k, v in OrderedDict(sorted(val.items(), key=itemgetter(0))).items():
                    result += (encode_str(k) + encode_(v))

                result += encode('e', val_encoding)

            elif isinstance(val, byte_types):
                result = encode('%s:' % len(val), val_encoding)
                result += val

            else:
                raise BencodeEncodingError('Unable to encode `%s` %s' % (type(val), val))

            return result

        return encode_(value)

    @classmethod
    def decode(cls, encoded):
        """Decodes bencoded data introduced as bytes.

        Returns decoded structure(s).

        :param bytes encoded:
        """
        def create_dict(items):
            # Let's guarantee that dictionaries are sorted.
            k_v_pair = zip(*[iter(items)] * 2)
            return OrderedDict(sorted(k_v_pair, key=itemgetter(0)))

        def create_list(items):
            return list(items)

        stack_items = []
        stack_containers = []

        def compress_stack():
            target_container = stack_containers.pop()
            subitems = []

            while True:
                subitem = stack_items.pop()
                subitems.append(subitem)
                if subitem is target_container:
                    break

            container_creator = subitems.pop()
            container = container_creator(reversed(subitems))
            stack_items.append(container)

        def parse_forward(till_char, sequence):
            number = ''
            char_sub_idx = 0

            for char_sub_idx, char_sub in enumerate(sequence):
                char_sub = chr_(char_sub)
                if char_sub == till_char:
                    break

                number += char_sub

            number = int(number or 0)
            char_sub_idx += 1

            return number, char_sub_idx

        while encoded:
            char = encoded[0]
            char = chr_(char)

            if char == 'd':  # Dictionary
                stack_items.append(create_dict)
                stack_containers.append(create_dict)
                encoded = encoded[1:]

            elif char == 'l':  # List
                stack_items.append(create_list)
                stack_containers.append(create_list)
                encoded = encoded[1:]

            elif char == 'i':  # Integer
                number, char_sub_idx = parse_forward('e', encoded[1:])
                char_sub_idx += 1

                stack_items.append(number)
                encoded = encoded[char_sub_idx:]

            elif char.isdigit():  # String
                str_len, char_sub_idx = parse_forward(':', encoded)
                last_char_idx = char_sub_idx + str_len

                string = encoded[char_sub_idx:last_char_idx]
                try:
                    string = string.decode('utf-8')
                except UnicodeDecodeError:
                    # Considered bytestring (e.g. `pieces` hashes concatenation).
                    pass

                stack_items.append(string)
                encoded = encoded[last_char_idx:]

            elif char == 'e':  # End of a dictionary or a list.
                compress_stack()
                encoded = encoded[1:]

            else:
                raise BencodeDecodingError('Unable to interpret `%s` char.' % char)

        if len(stack_items) == 1:
            stack_items = stack_items.pop()

        return stack_items

    @classmethod
    def read_string(cls, string):
        """Decodes a given bencoded string or bytestring.

        Returns decoded structure(s).

        :param str string:
        :rtype: list
        """
        if PY3 and not isinstance(string, byte_types):
            string = string.encode()

        return cls.decode(string)

    @classmethod
    def read_file(cls, filepath):
        """Decodes bencoded data of a given file.

        Returns decoded structure(s).

        :param str filepath:
        :rtype: list
        """
        with open(filepath, mode='rb') as f:
            contents = f.read()
        return cls.decode(contents)
