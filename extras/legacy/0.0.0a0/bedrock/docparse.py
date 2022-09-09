"""Parser for bedrock function docstrings

Docstrings can be used in bedrock commands
to document the function of the command.
The documentation will be included in the
help command.

The docstring uses the same syntax as in
numpydoc with less sections.

Code edited from
https://github.com/numpy/numpydoc/blob/main/numpydoc/docscrape.py

"""
import inspect
import textwrap
import re
from warnings import warn
from collections import namedtuple
from collections.abc import Callable, Mapping
import copy


def strip_blank_lines(l):
    "Remove leading and trailing blank lines from a list of lines"
    while l and not l[0].strip():
        del l[0]
    while l and not l[-1].strip():
        del l[-1]
    return l

def dedent_lines(lines):
    """Deindent a list of lines maximally"""
    return textwrap.dedent("\n".join(lines)).split("\n")


class Reader:
    """A line-based string reader.
    
    """
    def __init__(self, data):
        """
        Parameters
        ----------
        data : str
           String with lines separated by '\\n'.
        
        """
        if isinstance(data, list):
            self._str = data
        else:
            self._str = data.split('\n')  # store string as list of lines
        
        self.reset()
    
    def __getitem__(self, n):
        return self._str[n]
    
    def reset(self):
        self._l = 0  # current line nr
    
    def read(self):
        if not self.eof():
            out = self[self._l]
            self._l += 1
            return out
        else:
            return ''
    
    def seek_next_non_empty_line(self):
        for l in self[self._l:]:
            if l.strip():
                break
            else:
                self._l += 1
    
    def eof(self):
        return self._l >= len(self._str)
    
    def read_to_condition(self, condition_func):
        start = self._l
        for line in self[start:]:
            if condition_func(line):
                return self[start:self._l]
            self._l += 1
            if self.eof():
                return self[start:self._l+1]
        return []
    
    def read_to_next_empty_line(self):
        self.seek_next_non_empty_line()
    
        def is_empty(line):
            return not line.strip()
    
        return self.read_to_condition(is_empty)
    
    def read_to_next_unindented_line(self):
        def is_unindented(line):
            return (line.strip() and (len(line.lstrip()) == len(line)))
        return self.read_to_condition(is_unindented)
    
    def peek(self, n=0):
        if self._l + n < len(self._str):
            return self[self._l + n]
        else:
            return ''
    
    def is_empty(self):
        return not ''.join(self._str).strip()


class ParseError(Exception):
    def __str__(self):
        message = self.args[0]
        if hasattr(self, 'docstring'):
            message = f"{message} in {self.docstring!r}"
        return message


Parameter = namedtuple('Parameter', ['name', 'type', 'desc'])


class BedrockDocString(Mapping):
    """Parses a bedrockdoc string to an abstract representation
    
    Instances define a mapping from section title to structured data.
    
    """
    
    sections = {
        'Summary': [''],
        'Extended Summary': [],
        'Parameters': [],
        'Returns': [],
        'Raises': [],
        'Warns': [],
        'Other Parameters': [],
        'Notes': [],
        'Warnings': [],
        'References': '',
        'Examples': ''
    }
    
    def __init__(self, docstring, config=None):
        orig_docstring = docstring
        docstring = textwrap.dedent(docstring).split('\n')
        
        self._doc = Reader(docstring)
        self._parsed_data = copy.deepcopy(self.sections)
    
        try:
            self._parse()
        except ParseError as e:
            e.docstring = orig_docstring
            raise
    
    def __getitem__(self, key):
        return self._parsed_data[key]
    
    def __setitem__(self, key, val):
        if key not in self._parsed_data:
            self._error_location(f"Unknown section {key}", error=False)
        else:
            self._parsed_data[key] = val
    
    def __iter__(self):
        return iter(self._parsed_data)
    
    def __len__(self):
        return len(self._parsed_data)
    
    def _is_at_section(self):
        self._doc.seek_next_non_empty_line()
        
        if self._doc.eof():
            return False
        
        l1 = self._doc.peek().strip()  # e.g. Parameters
        
        l2 = self._doc.peek(1).strip()  # ---------- or ==========
        if len(l2) >= 3 and (set(l2) in ({'-'}, {'='}) ) and len(l2) != len(l1):
            snip = '\n'.join(self._doc._str[:2])+'...'
            self._error_location("potentially wrong underline length... \n%s \n%s in \n%s"\
                    % (l1, l2, snip), error=False)
        return l2.startswith('-'*len(l1)) or l2.startswith('='*len(l1))
    
    def _strip(self, doc):
        i = 0
        j = 0
        for i, line in enumerate(doc):
            if line.strip():
                break
    
        for j, line in enumerate(doc[::-1]):
            if line.strip():
                break
        
        return doc[i:len(doc)-j]
    
    def _read_to_next_section(self):
        section = self._doc.read_to_next_empty_line()
        
        while not self._is_at_section() and not self._doc.eof():
            if not self._doc.peek(-1).strip():  # previous line was empty
                section += ['']
            
            section += self._doc.read_to_next_empty_line()
        
        return section
    
    def _read_sections(self):
        while not self._doc.eof():
            data = self._read_to_next_section()
            name = data[0].strip()
            
            if len(data) < 2:
                yield StopIteration
            else:
                yield name, self._strip(data[2:])
    
    def _parse_param_list(self, content, single_element_is_type=False):
        content = dedent_lines(content)
        r = Reader(content)
        params = []
        while not r.eof():
            header = r.read().strip()
            if ' :' in header:
                arg_name, arg_type = header.split(' :', maxsplit=1)
                arg_name, arg_type = arg_name.strip(), arg_type.strip()
            else:
                if single_element_is_type:
                    arg_name, arg_type = '', header
                else:
                    arg_name, arg_type = header, ''
             
            desc = r.read_to_next_unindented_line()
            desc = dedent_lines(desc)
            desc = strip_blank_lines(desc)
            
            params.append(Parameter(arg_name, arg_type, desc))
        
        return params
    
    _role = r":(?P<role>(py:)?\w+):"
    _funcbacktick = r"`(?P<name>(?:~\w+\.)?[a-zA-Z0-9_\.-]+)`"
    _funcplain = r"(?P<name2>[a-zA-Z0-9_\.-]+)"
    _funcname = r"(" + _role + _funcbacktick + r"|" + _funcplain + r")"
    _funcnamenext = _funcname.replace('role', 'rolenext')
    _funcnamenext = _funcnamenext.replace('name', 'namenext')
    _description = r"(?P<description>\s*:(\s+(?P<desc>\S+.*))?)?\s*$"
    _func_rgx = re.compile(r"^\s*" + _funcname + r"\s*")
    _line_rgx = re.compile(
        r"^\s*" +
        r"(?P<allfuncs>" +        # group for all function names
        _funcname +
        r"(?P<morefuncs>([,]\s+" + _funcnamenext + r")*)" +
        r")" +                     # end of "allfuncs"
        r"(?P<trailing>[,\.])?" +   # Some function lists have a trailing comma (or period)  '\s*'
        _description)
    
    # Empty <DESC> elements are replaced with '..'
    empty_description = '..'
    
    def _parse_summary(self):
        """Grab summary"""
        if self._is_at_section():
            return
        
        # If several signatures present, take the last one
        while True:
            summary = self._doc.read_to_next_empty_line()
            summary_str = " ".join([s.strip() for s in summary]).strip()
            compiled = re.compile(r'^([\w., ]+=)?\s*[\w\.]+\(.*\)$')
            if compiled.match(summary_str):
                self['Signature'] = summary_str
                if not self._is_at_section():
                    continue
            break
        
        if summary is not None:
            self['Summary'] = summary
        
        if not self._is_at_section():
            self['Extended Summary'] = self._read_to_next_section()
    
    def _parse(self):
        self._doc.reset()
        self._parse_summary()
        
        sections = list(self._read_sections())
        section_names = set([section for section, content in sections])
        
        for (section, content) in sections:
            if not section.startswith('..'):
                section = (s.capitalize() for s in section.split(' '))
                section = ' '.join(section)
                if self.get(section):
                    self._error_location("The section %s appears twice in  %s"
                            % (section, '\n'.join(self._doc._str)))
            
            if section in ('Parameters', 'Other Parameters'):
                self[section] = self._parse_param_list(content)
            elif section in ('Returns', 'Raises', 'Warns'):
                self[section] = self._parse_param_list(
                    content, single_element_is_type=True)
            else:
                self[section] = content
    
    @property
    def _obj(self):
        if hasattr(self, '_cls'):
            return self._cls
        elif hasattr(self, '_f'):
            return self._f
        return None
    
    def _error_location(self, msg, error=True):
        if self._obj is not None:
            # we know where the docs came from:
            try:
                filename = inspect.getsourcefile(self._obj)
            except TypeError:
                filename = None
            # Make UserWarning more descriptive via object introspection.
            # Skip if introspection fails
            name = getattr(self._obj, '__name__', None)
            if name is None:
                name = getattr(getattr(self._obj, '__class__', None), '__name__', None)
            if name is not None:
                msg += f" in the docstring of {name}"
            msg += f" in {filename}." if filename else ""
        if error:
            raise ValueError(msg)
        else:
            warn(msg)
    
    # string conversion routines
    
    def _str_header(self, name, symbol='-'):
        return [name, len(name)*symbol]
    
    def _str_indent(self, doc, indent=4):
        return [' '*indent + line for line in doc]
    
    def _str_summary(self):
        if self['Summary']:
            return self['Summary'] + ['']
        return []
    
    def _str_extended_summary(self):
        if self['Extended Summary']:
            return self['Extended Summary'] + ['']
        return []
    
    def _str_param_list(self, name):
        out = []
        if self[name]:
            out += self._str_header(name)
            for param in self[name]:
                parts = []
                if param.name:
                    parts.append(param.name)
                if param.type:
                    parts.append(param.type)
                out += [' : '.join(parts)]
                if param.desc and ''.join(param.desc).strip():
                    out += self._str_indent(param.desc)
            out += ['']
        return out
    
    def _str_section(self, name):
        out = []
        if self[name]:
            out += self._str_header(name)
            out += self[name]
            out += ['']
        return out
    
        if last_had_desc:
            out += ['']
        out += ['']
        return out
    
    def __str__(self, func_role=''):
        out = []
        out += self._str_summary()
        out += self._str_extended_summary()
        for param_list in ('Parameters', 'Returns',
                           'Other Parameters', 'Raises', 'Warns'):
            out += self._str_param_list(param_list)
        out += self._str_section('Warnings')
        for s in ('Notes', 'Examples'):
            out += self._str_section(s)
        return '\n'.join(out)
