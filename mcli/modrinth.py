'''Hyper-minimalistic Modrinth mod searching API for python.

This module is soo not for public use...
'''

from annotationlib import get_annotations
from enum import StrEnum, auto
from requests import HTTPError
import requests

APIURL = 'https://api.modrinth.com/v2'

# Coding? more like multi-level developer / program torturing...
def _jsonclass(cls):
	'''Like `@dataclass` but less fucked and more fucked...'''
	#superinit = cls.__init__
	def init(self, **kwargs):
		#superinit(self)
		for prop in get_annotations(cls).keys():
			if kwargs.get(prop, None) is not None:
				setattr(self, prop, kwargs[prop])
	cls.__init__ = init
	return cls

class Category(StrEnum):
	'''Categories a project falls under.'''
	ADVENTURE = auto()
	CURSED = auto()
	DECORATION = auto()
	ECONOMY = auto()
	EQUIPMENT = auto()
	FOOD = auto()
	LIBRARY = auto()
	MAGIC = auto()
	MANAGEMENT = auto()
	MINIGAME = auto()
	MOBS = auto()
	OPTIMIZATION = auto()
	SOCIAL = auto()
	STORAGE = auto()
	TECHNOLOGY = auto()
	TRANSPORTATION = auto()
	UTILITY = auto()
	WORLDGEN = auto()
	MISC = auto()

	@classmethod
	def list(cls, l: list[str]):
		'''Convert `l` into type `list[Category]`'''
		return [Category[t.upper()] if getattr(Category, t.upper(), '') else Category.MISC for t in l]

class Loader(StrEnum):
	'''Loaders that a project supported.'''
	FABRIC = auto()
	FORGE = auto()
	QUILT = auto()
	NEOFORGE = auto()
	UNSUPPORTED = auto()

	@classmethod
	def list(cls, l: list[str]):
		'''Convert `l` into type `list[Loader]`'''
		return [Loader[t.upper()] if getattr(Loader, t.upper(), '') else Loader.UNSUPPORTED for t in l]

class ProjectType(StrEnum):
	'''Type of a project.'''
	MOD = auto()
	MODPACK = auto()
	RESOURCEPACK = auto()
	SHADER = auto()

class FileType(StrEnum):
	'''Type of .File can be.'''
	REQUIRED_RESOURCE_PACK = 'required-resource-pack'
	OPTIONAL_RESOURCE_PACK = 'optional-resource-pack'
	SOURCES_JAR = 'sources-jar'
	DEV_JAR = 'dev-jar'
	JAVADOC_JAR = 'javadoc-jar'
	UNKNOWN = 'unknown'


@_jsonclass
class File:
	'''A modrinth kind of file.'''
	url: str
	filename: str
	size: str
	file_type: FileType = FileType.UNKNOWN

@_jsonclass
class Project:
	'''A project in modrinth.'''
	id: str
	slug: str
	title: str
	downloads: int
	desc: str = ''
	description: str = ''
	type: ProjectType = ProjectType.MOD
	categories: list[Category] = []
	loaders: list[Loader] = []
	versions: list[str] = []
	game_versions: list[str] = []

	def __repr__(self) -> str:
		return f'<ModrinthProject "{self.slug}">'

	def latestver(self) -> str:
		'''Return a game version that this project support.'''
		return list(self.game_versions).pop()

	def prettyprint(self) -> None:
		'''Print this project in a pretty way.'''
		print(
			f'{self.title} ({self.type}:{self.slug}:{self.latestver()}):\n{self.description}'
		)

	@classmethod
	def fromdict(cls, d: dict):
		'''Create `Project`.'''
		d['categories'] = Category.list(d['categories'])
		d['loaders'] = Loader.list(d['loaders']) if d.get('loaders') else []

		# NOTE: searched project has some different keys then ones gathered from /project.
		if d.get('project_id', ''): # if this is from search
			d['id'] = d['project_id']
			d['type'] = d['project_type']
			d['desc'] = d['description']
			d['game_versions'] = d['versions']

		return cls(**d)

@_jsonclass
class ProjectVersion:
	'''A version of a project.'''
	project_id: str
	id: str
	name: str
	version_number: str
	files: list[File] = []

	@classmethod
	def fromdict(cls, d: dict):
		'''Create `ProjectVersion`'''
		d['files'] = [File(**f) for f in d['files']]
		return cls(**d)

	def __repr__(self) -> str:
		return f'<ProjectVersion {self.project_id}:{self.name}>'

@_jsonclass
class Search:
	'''A result of a `search()`.'''
	queried: str
	hits: list[Project]
	offset: int
	limit: int
	total_hits: int

	@classmethod
	def fromdict(cls, d: dict):
		'''Create `Search`.'''
		d['hits'] = [Project.fromdict(proj) for proj in d['hits']]
		return cls(**d)

def search(query: str, forloader: str = '', formcver: str = '') -> Search:
	'''Search for projects.'''
	r = requests.get(
		APIURL + '/search',
		{
			'query': query
		} | ({
			'facets': f'[["categories:{forloader}"],["versions:{formcver}"]]'
		} if forloader else {}),
		timeout=5000
	)

	if not r.ok:
		raise requests.HTTPError(f'Error requesting a search: {r.text}')

	d = r.json()
	d['queried'] = query

	return Search.fromdict(d)

def get_project(slugid: str) -> Project:
	'''Get a project.'''
	r = requests.get(APIURL + f'/project/{slugid}', timeout=5000)

	if not r.ok:
		raise HTTPError(f'Error requesting the project ({slugid}): {r.text}')

	d = r.json()
	return Project.fromdict(d)

def get_project_versions(slugid: str, forloader: str = '', formcver: str = '') -> list[ProjectVersion]:
	r = requests.get(
		f'{APIURL}/project/{slugid}/version',
		{
			'loaders': f'["{forloader}"]',
			'game_versions': f'["{formcver}"]',
		} if forloader else None,
		timeout=5000
	)

	if not r.ok:
		raise HTTPError(
			f'Error requesting verions for project ({slugid})'
			f' with params ({forloader}, {formcver})' if forloader else ''
			f': {r.json()}'
		)

	l = r.json()

	return [ProjectVersion.fromdict(d) for d in l]
