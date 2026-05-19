'''Top level library.'''

from annotationlib import get_annotations

# Coding? more like multi-level developer / program torturing...
def jsonclass(cls):
	'''Like `@dataclass` but less fucked and more fucked...'''
	#superinit = cls.__init__
	def init(self, **kwargs):
		#superinit(self)
		for prop in get_annotations(cls).keys():
			if kwargs.get(prop, None) is not None:
				setattr(self, prop, kwargs[prop])
	cls.__init__ = init
	return cls

