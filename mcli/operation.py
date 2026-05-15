'''mcli's operations.'''

from sys import stdout
from os import path
from mcli.modrinth import search as mrsearch, get_project_versions as get_mrproject_versions
import requests

def search(query: str, forloader: str = '', formcver: str = '') -> None:
	'''Search for Modrinth projects and print them.'''
	stdout.write(
		f'Searching Modrinth for "{query}"' + (
			f' for "{forloader}({formcver})".' if forloader else '.'
		)
	)
	stdout.flush()

	s = mrsearch(query, forloader, formcver)

	if not s.total_hits:
		print('\33[2K\rNo project found.')
	else:
		print(f'\33[2K\rFound {s.total_hits} projects:\n')
		for hit in s.hits:
			hit.prettyprint()
			print()
		print(f'{s.offset} to {min(s.offset + s.limit, s.total_hits)} out of {s.total_hits}.')

def download(slugid: str, outdir: str, /, forloader: str = '', formcver: str = '') -> None:
	'''Download `slugid` into `outdir`.'''
	vers = get_mrproject_versions(slugid, forloader, formcver)

	if not vers:
		return

	if len(vers) > 1:
		print('There are multiple versions, selecting latest.')
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

