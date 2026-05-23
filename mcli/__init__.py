'''Core mcli stuff.'''

from mcli import operation
from mcli import modrinth
from mcli.minecraft import Instance
from mcli.cli import Cmd
from mcli.meta import Dot, instanceprojecttypefolder

def search(
	query: str,
	instance: Instance,
	*,
	perpage: int = 10,
	page: int = 0,
) -> None:
	'''Interfaced `operation.search`.'''
	if not instance:
		operation.search(query, limit=perpage, offset=perpage*page)
	else:
		operation.search(
			query,
			loader=instance.loader,
			mcver=instance.version,
			limit=perpage,
			offset=perpage*page
		)

def download(slugid: str, instance: Instance, dot: Dot) -> None:
	'''Interfaced `operation.download`.'''
	if not instance:
		operation.download(slugid, './')

	proj = modrinth.get_project(slugid)

	downpath = instanceprojecttypefolder(project=proj, instance=instance)

	if downpath:
		operation.download(
			slugid,
			downpath,
			loader=instance.loader,
			mcver=instance.version,
			dot=dot,
			project=proj
		)
		fix_dependencies(instance, dot)
	else:
		raise TypeError(f'Project "{proj.slug}" is of type "{proj.type}", download is unsupported.')

def remove(slugid: str, instance: Instance, dot: Dot) -> None:
	'''Interfaced `operation.remove`.'''
	operation.remove(slugid, instance, dot)

def fix_dependencies(instance: Instance, dot: Dot) -> None:
	'''Check packages missing dependencies and download them.'''
	if not dot:
		raise EnvironmentError(f'mcli did not initialize properly. "{dot.packagejson}" not found.')

	for pkg in dot.packages:
		for dep in pkg.dependencies:
			if dep not in [pk.id for pk in dot.packages]:
				download(dep, instance, dot)

class MCmd(Cmd):
	'''mcli's custom Cmd.'''

	SWITCHSPECS = [
		'h/help: Print help for the command.',
		'perpage=NUMBER: For `search`, print `NUMBER` of entry. Default 10.',
		'page=NUMBER: For `search`, print entries at page `NUMBER`. Default 0.',
	]

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
		perpage = 10
		page = 0

		if self.switches['perpage']:
			perpage = int(self.switches['perpage'].value)
		if self.switches['page']:
			page = int(self.switches['page'].value)

		search(
			' '.join(args),
			self.instance,
			perpage=perpage,
			page=page
		)

	def do_download(self, args: list[str]) -> None:
		'''download|install|d|i [slugid...]: Download and install a project like [slugid...].'''
		for arg in args:
			download(arg, self.instance, self.dot)

	def do_remove(self, args: list[str]) -> None:
		'''remove|rm [slugid...]: Delete installed projects like [slugid...].'''
		for arg in args:
			remove(arg, self.instance, self.dot)

	def do_status(self, _: list[str]) -> None:
		'''status: Print environment status.'''
		print(f'{self.instance.loader}({self.instance.version}) at "{self.instance.path}"')

	def do_list(self, args: list[str]) -> None:
		'''list|ls [slugid...]: Print installed project like [slugid...].'''
		operation.list_packages(' '.join(args), self.dot)
