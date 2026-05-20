'''Module handling Minecraft related stuff.'''

import re
from os import path
from mcli.modrinth import Loader

class Instance:
	'''An object holding a Minecraft instance properties.'''
	def __init__(self, folder: str) -> None:
		self.path: str = folder
		self.version: str = ''
		self.loader: Loader = Loader.UNSUPPORTED
		self.probe()

	def probe(self) -> None:
		'''Auto fill `self.version` and `self.loader` based of `self.path`.'''
		latestlog = path.join(self.logfolder, 'latest.log')

		if not path.exists(latestlog):
			return

		with open(latestlog, 'r', encoding='utf8') as log:
			loghead = log.readline()

			def valid(mdat: re.Match|None) -> bool:
				if not mdat:
					return False
				return mdat.group('loader').lower() in Loader

			matchdat = re.search( # fabric log regex.
				'^.*?Loading Minecraft (?P<mcver>.*?) with (?P<loader>.*?) Loader (?P<loaderver>.*?)$',
				loghead
			)
			matchdat = re.search( # neoforge log regex.
				r'^.*?--version, (?P<loader>.*?)-(?P<loaderver>.*?), .*?--fml\.mcVersion, (?P<mcver>.*?), .*?$',
				loghead
			) if not valid(matchdat) else matchdat
			matchdat = re.search( # forge log regex.
				'^.*?--version, (?P<mcver>.*?)-(?P<loader>.*?)-(?P<loaderver>.*?),.*?$',
				loghead
			) if not valid(matchdat) else matchdat

			if matchdat:
				self.version = matchdat.group('mcver')
				self.loader = Loader(matchdat.group('loader').lower())

	def is_valid(self) -> bool:
		'''Return whether this instance is a Minecraft instance.'''
		return path.exists(self.logfolder) and \
			path.exists(self.savefolder) and \
			path.exists(self.configfolder)

	@property
	def modfolder(self) -> str:
		'''Mod folder.'''
		return path.join(self.path, 'mods')

	@property
	def logfolder(self) -> str:
		'''Log folder.'''
		return path.join(self.path, 'logs')

	@property
	def savefolder(self) -> str:
		'''Save folder.'''
		return path.join(self.path, 'saves')

	@property
	def configfolder(self) -> str:
		'''Config folder.'''
		return path.join(self.path, 'config')

	@property
	def resourcepackfolder(self) -> str:
		'''Resource pack folder.'''
		return path.join(self.path, 'resourcepacks')

	@property
	def shaderfolder(self) -> str:
		'''Shader folder.'''
		return path.join(self.path, 'shaderpacks')

	def __bool__(self) -> bool:
		return self.is_valid()

	def __repr__(self) -> str:
		return f'<MinecraftInstance {f'{self.loader}:{self.version}' if self.is_valid() else 'invalid'}>'
