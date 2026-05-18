'''Core mcli stuff.'''

from mcli import operation
from mcli import modrinth
from mcli.minecraft import Instance
from mcli.cli import Cmd
from mcli.meta import Dot

def search(query: str, instance: Instance) -> None:
	'''Interfaced `operation.search`.'''
	if not instance:
		operation.search(query)
	else:
		operation.search(query, loader=instance.loader, mcver=instance.version)

def download(slugid: str, instance: Instance, dot: Dot) -> None:
	'''Interfaced `operation.download`.'''
	if not instance:
		operation.download(slugid, './')

	proj = modrinth.get_project(slugid)

	downpath = ''
	match proj.type:
		case modrinth.ProjectType.MOD:
			downpath = instance.modfolder
		case modrinth.ProjectType.SHADER:
			downpath = instance.shaderfolder
		case modrinth.ProjectType.RESOURCEPACK:
			downpath = instance.resourcepackfolder

	if downpath:
		operation.download(
			slugid,
			downpath,
			loader=instance.loader,
			mcver=instance.version,
			dot=dot,
			project=proj
		)
	else:
		raise TypeError(f'Project "{proj.slug}" is of type "{proj.type}", download is unsupported.')

def remove(slugid: str, dot: Dot) -> None:
	'''Interfaced `operation.remove`.'''
	operation.remove(slugid, dot)

class MCmd(Cmd):
	'''mcli's custom Cmd.'''
	def __init__(self, instance: Instance, dot: Dot) -> None:
		super().__init__()

		self.instance = instance
		self.dot = dot

	def do_help(self, args: list[str]) -> None:
		'''help|h [what]: print help.'''
		if args:
			for arg in args:
				if arg in self.commands:
					print(self.commands[arg].__doc__)
				else:
					raise LookupError(f'No help of "{arg}"')
			return

		printed = []
		for cmd in self.commands.values():
			if not cmd in printed:
				print(cmd.__doc__)
				printed.append(cmd)

	def do_search(self, args: list[str]) -> None:
		'''search|find|s|f [query...]: Search for projects like [query...].'''
		search(' '.join(args), self.instance)

	def do_download(self, args: list[str]) -> None:
		'''download|install|d|i [slugid...]: Download and install a project like [slugid...].'''
		for arg in args:
			download(arg, self.instance, self.dot)

	def do_remove(self, args: list[str]) -> None:
		'''remove|rm [slugid...]: Delete installed projects like [slugid...].'''
		for arg in args:
			remove(arg, self.dot)

	def do_status(self, args: list[str]) -> None:
		'''status: Print environment status.'''
		print(f'{self.instance.loader}({self.instance.version}) at "{self.instance.path}"')
