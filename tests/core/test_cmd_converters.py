import sys
import typing
import unittest

from bedrock import commands

def conv(*args):
    return list(commands.convert_args(*args))

class ConvertCase(unittest.TestCase):
    
    def test_no_converters(self):
        def f(_, a, b, c):
            pass
        
        self.assertEqual(
            conv(
                ["foo", "2.5", "3"],
                f
            ),
            ["foo", "2.5", "3"]
        )
    
    def test_basic_converters(self):
        def f(_, a: str, b, c: int):
            pass
        
        self.assertEqual(
            conv(
                ["foo", "2.5", "3"],
                f
            ),
            ["foo", "2.5", 3]
        )
        
        with self.assertRaises(commands.BadArgumentError):
            conv(
                ["foo", "2.5", "bar"],
                f
            )
    
    def test_alotta_args(self):
        def f(_, a, b):
            pass
        
        with self.assertRaises(commands.TooManyArgumentsError):
            conv(
                ["foo", "bar", "baz"],
                f
            )
    
    def test_default_params(self):
        def f(_, a, b, c = "default"):
            pass
        
        self.assertEqual(
            conv(
                ["foo", "bar"],
                f
            ),
            ["foo", "bar"]
        )
        
        self.assertEqual(
            conv(
                ["foo", "bar", "baz"],
                f
            ),
            ["foo", "bar", "baz"]
        )
    
    def test_missing_args(self):
        def f(_, a, b, c):
            pass
        
        with self.assertRaises(commands.MissingArgumentsError):
            conv(
                ["foo"],
                f
            )
    
    def test_union(self):
        functions = []
        
        if sys.version_info[:2] >= (3, 10):
            def pep0604(_, a: int | float):
                pass
            
            functions.append(pep0604)
        
        def pep0484(_, a: typing.Union[int, float]):
            pass
        
        functions.append(pep0484)
        
        for f in functions:
            with self.subTest(case=f):
                self.assertEqual(
                    conv(
                        ["3"],
                        f
                    ),
                    [3]
                )
                
                self.assertEqual(
                    conv(
                        ["2.5"],
                        f
                    ),
                    [2.5]
                )
                
                with self.assertRaises(commands.BadArgumentError):
                    conv(
                        ["hi"],
                        f
                    )

if __name__ == '__main__':
    unittest.main()
