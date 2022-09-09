import unittest
from functools import partial

from bedrock.utils import boolean

class BoolConvertCase(unittest.TestCase):
    
    def test_default_true(self):
        self.assertEqual(
            boolean("trUe"),
            True
        )
        
        self.assertEqual(
            boolean("yeS"),
            True
        )
    
    def test_default_false(self):
        self.assertEqual(
            boolean("fAlSe"),
            False
        )
        
        self.assertEqual(
            boolean("no"),
            False
        )
    
    def test_invalid(self):
        with self.assertRaises(ValueError):
            boolean("definitely")
    
    def test_duplicate(self):
        mybool = partial(
            boolean,
            true = ["foo", "bar"],
            false = ["baz", "foo"]
        )
        
        with self.assertRaises(ValueError):
            mybool("invalid")
        
        with self.assertRaises(ValueError):
            mybool("bar")
        
    
    def test_custom_true(self):
        mybool = partial(
            boolean,
            true = ["y", "yes", "true"]
        )
        
        self.assertEqual(
            mybool("YeS"),
            True
        )
    
    def test_custom_false(self):
        mybool = partial(
            boolean,
            false = ["n", "no", "false"]
        )
        
        self.assertEqual(
            mybool("faLSe"),
            False
        )

if __name__ == '__main__':
    unittest.main()
