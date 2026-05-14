'''mcli's operations.'''

from sys import stdout
from mcli.modrinth import search as mrsearch

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

