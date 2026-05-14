'''Entry for mcli.'''

from mcli import operation

if __name__ == '__main__':
	while True:
		cmd, txt = input(" > ").split(None, 1)

		match cmd:
			case 'search' | 'find':
				operation.search(txt)
