'''mcli's operations.'''

import os
from sys import stdout
from os import path
import requests
from mcli import modrinth
from mcli.meta import Dot

def search(
	query: str,
	*,
	offset: int = 0,
	limit: int = 10,
	loader: str = '',
	mcver: str = ''
) -> None:
	'''Search for Modrinth projects and print them.'''
	que = f' with "{query}"' if query else ''
	lod = f' for "{loader}({mcver})"' if loader and mcver else ''

	stdout.write(
		f'Searching Modrinth{que}{lod}.'
	)
	stdout.flush()

	s = modrinth.search(
		query,
		offset=offset,
		limit=limit,
		forloader=loader,
		formcver=mcver
	)

	if not s.total_hits:
		print(f'\33[2K\rNo project found{que}{lod}.')
	else:
		print(f'\33[2K\rFound {s.total_hits} projects{que}{lod}:\n')
		for hit in s.hits:
			hit.prettyprint()
			print()
		print(f'{s.offset} to {min(s.offset + s.limit, s.total_hits)} out of {s.total_hits}.')

def download(
	slugid: str,
	outdir: str,
	*,
	loader: str = '',
	mcver: str = '',
	dot: Dot | None = None,
	project: modrinth.Project | None = None
) -> None:
	'''Download `slugid`.'''

	vers = modrinth.get_project_versions(slugid, loader, mcver)

	if not vers:
		return

	ver = vers[0]

	for file in ver.files:
		with requests.get(file.url, stream=True, timeout=5000) as down:
			left = 0
			with open(path.join(outdir, file.filename), 'wb') as output:
				for chunk in down.iter_content(chunk_size=1024):
					left += 1024
					output.write(chunk)
					stdout.write(f'\33[2K\rDownloading "{file.filename}": {min(left/file.size*100, 100):.2f}%')
		stdout.write(f'\33[2K\rDownloaded "{file.filename}"\n')

	proj = project if project else modrinth.get_project(slugid)

	if dot:
		dot.set_package(proj, [path.abspath(path.join(outdir, file.filename)) for file in ver.files])

def remove(slugid: str, dot: Dot) -> None:
	'''Remove `slugid`.'''
	if not dot:
		raise EnvironmentError(f'mcli did not initialize properly. "{dot.packagejson}" not found.')

	for pkg, files in dot.packages.items():
		if dot.slugidmatch(slugid, pkg):
			for file in files:
				os.remove(file)
				print(f'Deleted "{file}"')
			break

	dot.remove_package(slugid)

def list_packages(query: str, dot: Dot) -> None:
	'''List downloaded package.'''
	if not dot:
		raise EnvironmentError(f'mcli did not initialize properly. "{dot.packagejson}" not found.')

	for pkg in dot.packages.keys():
		if query:
			if query in pkg:
				print(pkg)
		else:
			print(pkg)

