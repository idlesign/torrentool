import sys
import os
import unittest


DIR_CURRENT = os.path.abspath(os.path.dirname(__file__))
DIR_PARENT = os.path.dirname(DIR_CURRENT)

sys.path.insert(0, DIR_PARENT)

tests_loader = unittest.TestLoader()
test_suit = tests_loader.discover(DIR_CURRENT)
unittest.TextTestRunner().run(test_suit)
