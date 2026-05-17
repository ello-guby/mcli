'''Entry for mcli.'''

import sys
import os
import mcli
from mcli import minecraft

if __name__ == '__main__':
	args = sys.argv
	# its 'python mcli path/to/instance', pop will remain instance's path
	args.pop(0) 

	instancepath = os.getcwd()

	if args:
		if os.path.exists(args[0]):
			instancepath = args.pop(0)

	cmd = mcli.MCmd(minecraft.Instance(instancepath))
	if not args:
		cmd.cli()
	else:
		cmd.process(args)
