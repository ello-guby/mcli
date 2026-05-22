'''Im not sure where to put this...'''

import json
import os
from os import path
from mcli import modrinth
from mcli.lib import jsonclass
from mcli.minecraft import Instance

def instanceprojecttypefolder(
	projecttype: modrinth.ProjectType = modrinth.ProjectType.MOD,
	*,
	project: modrinth.Project|None = None,
	instance: Instance|None = None
) -> str:
	'''Return `instance`'s folder path that `project` target.'''
	if project is not None:
		projecttype = project.type
	if instance is None:
		instance = Instance('') # dummy instance

	match projecttype:
		case modrinth.ProjectType.MOD:
			return instance.modfolder
		case modrinth.ProjectType.SHADER:
			return instance.shaderfolder
		case modrinth.ProjectType.RESOURCEPACK:
			return instance.resourcepackfolder
	return ''

@jsonclass
class Package:
	'''For storing downloaded project data.'''
	slug: str
	id: str
	files: list[str] = []
	dependencies: list[str] = []

	@classmethod
	def fromprojectversion(cls, project: modrinth.Project, version: modrinth.ProjectVersion):
		'''Create `Package` from `project` and `version`'''
		d: dict = {}
		i = Instance('') # dummy instance to get paths for files.

		fp = instanceprojecttypefolder(project=project, instance=i)

		d['slug'] = project.slug
		d['id'] = project.id
		d['files'] = [path.join(fp, f.filename) for f in version.files]
		d['dependencies'] = version.dependencies

		return cls(**d)

class Dot:
	'''mcli's dotdir manager. Work by attaching itself on a minecraft instance.'''
	def __init__(self, instance: Instance) -> None:
		self.instance = instance
		self.packages: list[Package] = []

		if instance:
			if not path.exists(self.folder):
				os.mkdir(self.folder)

			if not path.exists(self.packagejson):
				with open(self.packagejson, 'xt', encoding='utf8'):
					pass
			else:
				with open(self.packagejson, 'rt', encoding='utf8') as file:
					txt = file.read()
					if txt:
						self.packages = [Package(**d) for d in json.loads(txt)['packages']]

	def set_package(self, project: modrinth.Project, version: modrinth.ProjectVersion) -> None:
		'''set downloaded data into the package.json file.'''
		self.packages.append(Package.fromprojectversion(project, version))
		self.packagesave()

	def remove_package(self, slugid: str) -> None:
		'''Remove data from the package.json file.'''
		for p in self.packages:
			if (
				modrinth.isslug(slugid) and p.slug == slugid
			) or (
				modrinth.isid(slugid) and p.id == slugid
			):
				self.packages.remove(p)
				self.packagesave()
				break

	def packagesave(self) -> None:
		'''Save the packages data.'''
		if self.instance:
			with open(self.packagejson, 'wt', encoding='utf8') as file:
				file.write(json.dumps({'packages': [p.__dict__ for p in self.packages]}, indent=2))

	@property
	def folder(self) -> str:
		'''mcli's folder'''
		return path.join(self.instance.path, '.mcli')

	@property
	def packagejson(self) -> str:
		'''json file to write package data.'''
		return path.join(self.folder, 'package.json')

	def __bool__(self) -> bool:
		return self.instance.is_valid()
