'''A Command Line Interface related library.'''

from typing import Any, Callable, NamedTuple

# A switch specification type: 'h/help' thing.
SwitchSpec = str

class Switch(NamedTuple):
	'''A switch of cmd arguments. Create one with `Switch.fromspec()`'''
	# 't/test=SOMETHING: Try test with `SOMETHING`'
	short: str             # t
	long: str              # test
	capturing: bool        # True
	placeholder: str       # SOMETHING
	description: str       # Try test with `SOMETHING`
	switched: bool = False # True after `SwitchParser(...).parse(a)` and `a` has '-t' or '--test'.
	value: str = ''        # The value taken.

	def switch(self, on: bool):
		'''Return duplicated with `self.switched = on`.'''
		s: list = list(self)
		s[5] = on
		return Switch(*s)

	def capture(self, value: str) -> Switch:
		'''Return duplicated with `self.captured = what`.'''
		s: list = list(self)
		s[6] = value
		return Switch(*s)

	@staticmethod
	def fromspec(spec: SwitchSpec) -> Switch:
		'''
		Build `Switch` from a spec string (`'o/option=OPTION: do option.'`) into:
		```
		Switch(
			short:       'o',
			long:        'option',
			capturing:   True,
			placeholder: 'OPTION',
			description: 'do option.',
		)
		```
		'''
		short = ''
		long = ''
		capturing = False
		placeholder = ''
		description = ''

		if ':' in spec:
			spec, description = spec.split(':', 1)

		if '=' in spec:
			spec, placeholder = spec.split('=', 1)
			capturing = True

		if '/' in spec:
			short, long = spec.split('/', 1)
		else:
			long = spec

		return Switch(short, long, capturing, placeholder, description)

	def __bool__(self) -> bool:
		return self.switched

	def __gt__(self, value) -> bool:
		return self.long > value.long

	def __lt__(self, value) -> bool:
		return self.long < value.long

	def __repr__(self) -> str:
		return f'<Switch "' \
		f'{f'{self.short}/' if self.short else ''}' \
		f'{self.long}' \
		f'{f'={self.placeholder}' if self.capturing else ''}' \
		f'{f':{self.description}' if self.description else ''}">'

class SwitchParser:
	'''
	A class to handle dash prefixed command line arguments.
	Usage example:
	```
	switch = SwitchParser('h/help: Display help', 'i/input=INPUT: Take `INPUT`')
	switch.process(['cmd', '-h'])
	
	if switch['help'].switched:
		showhelp()

	if switch['input'].switched:
		input = switch['input'].captured
	```
	mcli's takes on python's `argparse.ArgumentParser`.
	Switch specification syntax takes from [https://fishshell.com/docs/current/cmds/argparse.html]
	but limited.
	'''
	def __init__(self, *specs: SwitchSpec) -> None:
		self.switches = [Switch.fromspec(s) for s in specs]
		self._switchcheck()

	def __getitem__(self, key: str) -> Switch:
		return self.findswitch(key)

	def __delitem__(self, key: str) -> None:
		return self.removeswitch(key)

	def _switchcheck(self) -> None:
		self.switches.sort()

		for a, aswitch in enumerate(self.switches):

			if len(aswitch.short) > 1:
				raise NameError(f'Spec at index {a} is not a character ("{aswitch.short}").')

			if len(aswitch.long) <= 1:
				raise NameError(f'Switch at index {a} has very short long ("{aswitch.long}").')

			for b, bswitch in enumerate(self.switches):
				if a == b:
					continue

				if aswitch.long == bswitch.long:
					raise NameError(
						f'Switch at index {a} has the same long '
						f'as the one at idx {b} ("{aswitch.long}").'
					)

				if aswitch.short == bswitch.short:
					raise NameError(
						f'Switch at index {a} has same short as '
						f'the one at idx {b} ("{aswitch.short}").'
					)

	def addswitch(self, switch: Switch | SwitchSpec) -> None:
		'''Add a switch. Raise `NameError` if switches had non-unique name.'''
		if isinstance(switch, SwitchSpec):
			switch = Switch.fromspec(switch)
		self.switches.append(switch)
		self._switchcheck()

	def removeswitch(self, switch: str | Switch) -> None:
		'''Remove a switch. Raise `LookupError` if the switch is not found.'''
		if isinstance(switch, str):
			switch = self.findswitch(switch)
		self.switches.remove(switch)

	def process(self, args: list[str]) -> list[str]:
		'''Consume any '-' or '--' prefixed from `args` and switch them.'''

		pargs: list[str] = [] # processed arguments

		i = 0
		while i < len(args):
			arg = args[i]

			if not self.isswitch(arg):
				pargs.append(arg)
				i += 1
				continue

			short, key, capturing, value = self.switchparse(arg)

			if short:
				if capturing:
					raise ValueError(f'{arg} cannot assign value (not sure how to impl).')

				for char in key:
					self.switch(char, True)

			else:
				switch = self.findswitch(key)

				if switch.capturing and not capturing:             # if 'i=' '-i VALUE'
					i += 1
					value = args[i]

				elif switch.capturing and capturing and not value: # if 'i=' '-i='
					pass

				elif switch.capturing and capturing and value:     # if 'i=' '-i=value'
					pass

				elif not switch.capturing and capturing:           # if 'i' '-i='
					raise ValueError(f'{switch} does not capture.')

				self.switch(key, True, value)

			i += 1

		return pargs

	def reset(self) -> None:
		'''Reverse what `self.process()` has done.'''
		for switch in self.switches:
			self.switch(switch)

	def switch(self, switch: str | Switch, on = False, captured = '') -> None:
		'''
		Switch a switch from `self.switches` witch reference of `switch`.
		Optionally `captured`. Raise `LookupError` if no switch found.
		'''
		if isinstance(switch, str):
			switch = self.findswitch(switch)

		idx = self.switches.index(switch)
		self.switches.insert(idx, self.switches.pop(idx).switch(on).capture(captured))

	def findswitch(self, ref: str) -> Switch:
		'''
		Return a switch from `self.switches` with `ref`.
		Raise `LookupError` if none found.
		'''
		for switch in self.switches:
			comp = switch.short if len(ref) == 1 else switch.long

			if comp == ref:
				return switch

		raise LookupError(f'No switch with reference of "{ref}" found.')

	@staticmethod
	def isswitch(switch: str) -> bool:
		'''Wheather `switch` is a valid switch.'''
		return switch.startswith('-')

	@staticmethod
	def switchparse(switch: str) -> tuple[bool, str, bool, str]:
		'''
		Parse switch string (`'-o=option'` or `'--option=option'`) into:
		```
		(
			short:     True,     # If it's single dashed. `False` otherwise.
			key:       'o',      # Or 'option'.
			capturing: True,     # If '=' in the switch.
			value:     'option', # The captured value.
		)
		```
		Do `self.isswitch()` the switch before feed into this.
		'''
		short = True
		key = ''
		capturing = False
		value = ''

		switch = switch.strip()[1:]

		if switch.startswith('-'):
			switch = switch[1:]
			short = False

		if '=' in switch:
			key, value = switch.split('=', 1)
			capturing = True
		else:
			key = switch

		return short, key, capturing, value

class Cmd:
	'''
	mcli's takes on python's cmd.Cmd class.
	'''

	COMMAND_PREFIX = 'do_'

	def __init__(self) -> None:
		'''Create a new `Cmd`'''
		self.commands: dict[str, Callable] = {}

		for cmds in self._commands():
			print(self.parsedoc(cmds.__doc__))

	@classmethod
	def _commands(cls) -> list[dict[str, Any]]:
		'''
		Return all method with `COMMAND_PREFIX`ed name including super's method.
		Used for indexing commands.
		For actual commands, they're inside `self.commands`.
		'''
		r = []
		mro = cls.mro()
		mro = mro[0:len(mro) - 1]
		for clas in mro:
			for fname, fn in clas.__dict__.items():
				if fname.startswith(cls.COMMAND_PREFIX):
					r.append(fn)
		return r

	@staticmethod
	def parsedoc(docstr: str|None) -> tuple[list[str], list[str], str]:
		'''
		Parse document string like:
		```
		configure|config|conf|c [option] [value]:
		Configure [option] to be [value].
		If no [value], [option]'s value is echoed.
		If no [option], all option and their value are echoed.
		```
		into:
		```
		['configure', 'config', 'conf', 'c'],
		['[option]', '[value]'],
		'Configure [option] ...'
		```
		'''
		if not docstr:
			return [], [], ''

		cmds = ''
		args = ''
		desc = ''

		if ':' in docstr:
			docstr, desc = docstr.split(':', 1)
			desc = desc.strip('\n')

		if ' ' in docstr:
			cmds, args = docstr.split(' ', 1)
		else:
			cmds = docstr

		if ' ' in args:
			args = args.split(' ')
		else:
			args = [args]

		if '|' in cmds:
			cmds = cmds.split('|')
		else:
			cmds = [cmds]

		for i, v in enumerate(args):
			args[i] = v.strip()
		for i, v in enumerate(cmds):
			cmds[i] = v.strip()

		return cmds, args, desc
