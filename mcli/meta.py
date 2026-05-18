'''Im not sure where to put this...'''

import json
import os
from os import path
from mcli.minecraft import Instance

class Dot:
	'''mcli's dotdir manager. Work by attaching itself on a minecraft instance.'''
	def __init__(self, instance: Instance) -> None:
		self.instance = instance
		self.packages: dict[str, list[str]] = {}

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
						self.packages = json.loads(txt)

	def set_package(self, project_id: str, filenames: list[str]) -> None:
		'''set downloaded data into the package.json file.'''
		self.packages[project_id] = filenames
		self.packagesave()

	def remove_package(self, project_id: str) -> None:
		'''Remove data from the package.json file.'''
		del self.packages[project_id]
		self.packagesave()

	def packagesave(self) -> None:
		'''Save the packages data.'''
		if self.instance:
			with open(self.packagejson, 'wt', encoding='utf8') as file:
				file.write(json.dumps(self.packages, indent=2))

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
