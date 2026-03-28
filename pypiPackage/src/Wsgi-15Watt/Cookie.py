class Cookie(object):
	"""
	Representation of a HTTP cookie
	"""
	__key: str
	value: str
	__path: str

	def __init__(self, key: str, value: str, path: str = '/'):
		self.__key  = key
		self.value  = value
		self.__path = path


	@property
	def key(self) -> str:
		return self.__key


	@property
	def path(self) -> str:
		return self.__path


	def __str__(self):
		return "{key}={value};Path={path}".format(
			key=self.__key,
			value=self.value,
			path=self.__path
		)
