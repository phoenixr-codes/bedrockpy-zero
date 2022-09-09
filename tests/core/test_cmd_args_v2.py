import unittest
from bedrock import commands

class CommandArgsCase(unittest.TestCase):
    
    def test_simple_args(self):
        self.assertEqual(
            commands.get_command_args_v2("foo bar baz"),
            ["foo", "bar", "baz"]
        )
        
        self.assertEqual(
            commands.get_command_args_v2("foo"),
            ["foo"]
        )
    
    def test_quoted_args(self):
        self.assertEqual(
            commands.get_command_args_v2("foo \"bar\" baz 'foobar'"),
            ["foo", "bar", "baz", "foobar"]
        )
        
        self.assertEqual(
            commands.get_command_args_v2("foo \"bar baz\" foobar"),
            ["foo", "bar baz", "foobar"]
        )
    
    def test_quoted_quote(self):
        self.assertEqual(
            commands.get_command_args_v2("foo \"bar 'baz foobar' foobaz\""),
            ["foo", "bar 'baz foobar' foobaz"]
        )
    
    def test_unfinished_quoted_arg(self):
        with self.assertRaises(commands.MissingQuoteError):
            commands.get_command_args_v2("foo 'bar")
        
        with self.assertRaises(commands.MissingQuoteError):
            commands.get_command_args_v2("foo bar'")
    
    def test_alotta_spaces(self):
        self.assertEqual(
            commands.get_command_args_v2("foo bar    baz       foobar foobaz"),
            ["foo", "bar", "baz", "foobar", "foobaz"]
        )
    
    def test_no_args(self):
        self.assertEqual(
            commands.get_command_args_v2(""),
            []
        )
    
    def test_quote_symbol_as_arg(self):
        with self.assertRaises(commands.MissingQuoteError):
            commands.get_command_args_v2("foo ' ")
    
    def test_quoted_command_name(self):
        # you should use subcommands instead
        self.assertEqual(
            commands.get_command_args_v2("'foo bar' baz"),
            ["foo bar", "baz"]
        )
    
    
    def test_nonascii(self):
        self.assertEqual(
            commands.get_command_args_v2("foo bär båz"),
            ["foo", "bär", "båz"]
        )
    
    def test_nonutf8(self):
        self.assertEqual(
            commands.get_command_args_v2("foo \uD7FF baz"),
            ["foo", "\uD7FF", "baz"]
        )
        
    def test_empty_arg(self):
        self.assertEqual(
            commands.get_command_args_v2("foo '' baz"),
            ["foo", "", "baz"]
        )
    
if __name__ == '__main__':
    unittest.main()
