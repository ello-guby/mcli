'''Entry for mcli.'''

import sys
import os
import mcli
from mcli import minecraft
from mcli import meta

if __name__ == '__main__':
	args = sys.argv
	# its 'python mcli path/to/instance', pop will remain instance's path
	args.pop(0)

	instancepath = os.getcwd()

	if args:
		if os.path.exists(args[0]):
			instancepath = args.pop(0)

	instance = minecraft.Instance(instancepath)
	cmd = mcli.MCmd(instance, meta.Dot(instance))
	if not args:
		cmd.cli()
	else:
		cmd.process(args)
