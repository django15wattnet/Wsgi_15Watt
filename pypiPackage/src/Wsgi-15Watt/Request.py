from typing import Dict
from urllib.parse import unquote, parse_qs
from io import BytesIO

from .Route import HttpMethods
from .Route import Route
from .multipart import parse_form_data, MultipartPart
from .Exceptions import ParamNotFound, ValueNotFound, FileNotFound


class Request(object):
	"""
		Represents the http request.
	"""
	def __init__(self, env: dict, route: Route):
		self.__env        = env
		self.__header     = {}
		self.__user       = self.__user = env.get('REMOTE_USER', '')
		self.__password   = ''
		self.__route      = route
		self.__httpMethod = self.__httpMethod = env.get('REQUEST_METHOD', 'GET')
		self.__pathInfo   = env.get('PATH_INFO', '/')
		
		self.__params, self.__files = self.__getParameters(
			env,
			self.__route.getParamsFromPath(path=env.get('PATH_INFO'))
		)

		self.__requestBodySize = 0
		self.__requestBody     = ''

		try:
			self.__requestBodySize = int(self.__env.get('CONTENT_LENGTH', 0))
		except ValueError:
			pass
		except TypeError:
			pass

		byteIo = BytesIO(initial_bytes=env['wsgi.input'].read(self.__requestBodySize))

		# Read the requests body no matter what content type or method the request is
		byteIo.seek(0)
		self.__requestBody = unquote(byteIo.read(self.__requestBodySize).decode('utf-8'))
		byteIo.close()

		# Methode
		self.__requestMethod = self.__env.get('REQUEST_METHOD', 'GET')

		return
	
	
	@property
	def user(self) -> str:
		return self.__user
	
	
	@property
	def httpMethod(self) -> HttpMethods:
		return HttpMethods[self.__httpMethod]
	
	
	@property
	def pathInfo(self) -> str:
		return self.__pathInfo
	
	
	@property
	def env(self) -> dict:
		return self.__env
	
	
	@property
	def route(self) -> Route:
		"""
			Returns the route, that is responsible for this request.
		"""
		return self.__route


	def getRequestBody(self) -> str:
		return self.__requestBody


	def get(self, name: str):
		"""
			Returns the value of the parameter name.
			If there are multiple values with the same name, the first value is returned.

		:raise: ParamNotFound
		"""
		if name not in self.__params:
			raise ParamNotFound(returnMsg=f'Parameter {name} not found')

		if 0 == len(self.__params[name]):
			raise ParamNotFound(returnMsg=f'Parameter {name} is empty')

		return self.__params[name][0]


	def getAsList(self, name: str) -> list:
		"""
			Returns the list of values of the parameter name.

		:raise: ParamNotFound
		"""
		if name not in self.__params:
			raise ParamNotFound(returnMsg=f'Parameter {name} not found')

		if 0 == len(self.__params[name]):
			raise ParamNotFound(returnMsg=f'Parameter {name} is empty')

		return self.__params[name]


	def getDictParams(self) -> dict:
		"""
			Returns all parameters as a dictionary.
		"""
		return self.__params


	def has(self, name: str) -> bool:
		"""
			Checks if the parameter name exists.
		"""
		return name in self.__params


	def hasFile(self, name: str) -> bool:
		"""
			Checks if a file with the name exists.
		"""
		return name in self.__files


	def getFile(self, name: str) -> MultipartPart:
		"""
			Returns the file with the name.
		"""
		if name not in self.__files:
			raise FileNotFound(returnMsg=f'File {name} not found')

		return self.__files[name]


	def getDíctFiles(self) -> Dict[str, MultipartPart]:
		"""
			Returns all files as a dictionary.
		"""
		return self.__files


	def getHeader(self, name: str) -> str:
		"""
			Returns the value of the header field name.
		"""
		if name not in self.__header:
			raise ValueNotFound(returnMsg=f'Header-Field {name} not found')

		return self.__header[name]


	def hasHeader(self, name: str) -> bool:
		"""
			Check if there is a value for name in the header values.
		"""
		return name in self.__header


	def envHasKey(self, key: str) -> bool:
		"""
			Check if the key exists in the env-Dict
		"""
		return key in self.__env


	def getEnvByKey(self, key: str) -> str|None:
		"""
		Returns the value of key from the env-Dict or None.
		"""
		return self.__env.get(key, None)


	def __getParameters(self, env: dict, paramsFromRoute: dict) -> (dict, dict):
		"""
			Reads the parameters from all sources:
				- from the query string (GET)
				- from the request body (POST, PUT)
				- from the path (Route)

			Each parameter can have multiple values.
			Files will be stored as a parameter und in files
		"""
		dictParams = {}
		dictFiles  = {}

		# Add the parameters from the route
		for key in paramsFromRoute:
			dictParams[key] = [paramsFromRoute[key]]

		# Add the parameters from the query string
		queryParams = parse_qs(env.get('QUERY_STRING', ''))
		for item in queryParams.items():
			if item[0] in dictParams:
				dictParams[item[0]] += item[1]
			else:
				dictParams[item[0]] = item[1]

		# Add the parameters from the request body
		(dictForm, dictMultiFiles) = parse_form_data(environ=env)

		for key in dictForm:
			if key in dictParams:
				dictParams[key] += dictForm.getall(key)
			else:
				dictParams[key] = dictForm.getall(key)

		for key in dictMultiFiles:
			if key in dictParams:
				dictParams[key] += [dictMultiFiles[key]]
			else:
				dictParams[key] = [dictMultiFiles[key]]

			# Save files also separately
			dictFiles[key] = dictMultiFiles[key]

		return dictParams, dictFiles
