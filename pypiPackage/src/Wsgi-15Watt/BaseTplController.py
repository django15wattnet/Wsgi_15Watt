from .BaseController import BaseController


class BaseTplController(BaseController):
	"""
		Basisklasse aller AdmController
	"""
	def __init__(self, config: dict):
		super().__init__(config=config)

		if 'pathBase' in config:
			self._pathBase = config['pathBase']
		else:
			raise ValueError('pathBase not found in config')

		if 'pathTemplates' in config:
			self._pathTemplates = config['pathTemplates']
		else:
			raise ValueError('pathTemplates not found in config')


	def _loadTemplate(self, tplName: str) -> str:
		"""
			Lädt das Template
		"""
		strPath = self._pathTemplates + '/' + tplName
		with open(strPath, 'r', encoding='utf-8') as file:
			return file.read()


	def render(self, request, response):
		"""
			Generiert das Template
		"""
		response.contentType = 'text/html'
		response.returnCode = 200
		response.stringContent = self._tpl
		return