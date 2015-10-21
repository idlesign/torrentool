import sys
from collections import OrderedDict

from torrentool.exceptions import BencodeDecodingError


if sys.version_info >= (3, 0):
    chr_ = chr

else:
    chr_ = lambda ch: ch



class Bencode:
    """Exposes utilities for bencoding."""

    @classmethod
    def decode(cls, encoded):
        """Decodes bencoded data introduced as bytes.

        Returns a list with decoded structures.

        :param bytes encoded:
        :rtype: list
        """

        def create_dict(items):
            return OrderedDict(zip(*[iter(items)] * 2))

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
                last_char_idx = char_sub_idx+str_len

                string = encoded[char_sub_idx:last_char_idx]
                try:
                    string = string.decode()
                except UnicodeDecodeError:
                    pass

                stack_items.append(string)
                encoded = encoded[last_char_idx:]

            elif char == 'e':  # End of a dictionary or a list.
                compress_stack()
                encoded = encoded[1:]

            else:
                raise BencodeDecodingError('Unable to interpret `%s` char.' % char)

        return stack_items

    @classmethod
    def read_string(cls, string):
        """Decodes a given bencoded string.

        Returns a list with decoded structures.

        :param str string:
        :rtype: list
        """
        string = string.encode()
        return cls.decode(string)

    @classmethod
    def read_file(cls, filepath):
        """Decodes bencoded data of a given file.

        Returns a list with decoded structures.

        :param str filepath:
        :rtype: list
        """
        with open(filepath, mode='rb') as f:
            contents = f.read()
        return cls.decode(contents)
