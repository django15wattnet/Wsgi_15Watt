import traceback
from importlib import import_module
from .Request import Request
from .Response import Response
from .Route import HttpMethods, Route
from .Exceptions import Base


class Kernel(object):
	"""
		Handles the complete request to response cycle.
	"""
	def __init__(self, nameConfig: str = 'config', nameRoutes: str = 'routes'):
		"""
		Sets the names of the configuration and routes files.

		These files are expected to be in the project root.

		:param nameConfig: str

		:param nameRoutes: str
		"""
		self.__nameConfig = nameConfig
		self.__nameRoutes = nameRoutes
		self.__routes     = {}
		self._config      = {}
		self.__env        = {}
		
		self.__loadConfig()
		self.__loadRoutes()


	def run(self, env: dict, startResponse):
		"""
			Handles to whole request.

			Will be called by your application.py
		"""
		# Only needed for the __str__ method and debug purposes. DO NOT USE!
		self.__env = env

		# Iterate over all routes
		for idx in self.__routes:
			if not self.__routes[idx].match(path=env.get('PATH_INFO'), httpMethod=HttpMethods[env.get('REQUEST_METHOD')]):
				continue

			# Found, so I call the controller method
			request = Request(
				env=env,
				route=self.__routes[idx]
			)

			response = Response(
				startResponse=startResponse,
				request=request,
				route=self.__routes[idx]
			)

			response.addHeader('X-Framework', 'Wsgi by Thomas Siemion')
			self.__addAccessControlHeader(request=request, response=response)

			# Call the controller method
			try:
				self.__routes[idx].methodToCall(
					request=request,
					response=response
				)

			except Exception as e:
				if 'debug' in self._config and self._config['debug'] is True:
					tb = traceback.format_exc()
				else:
					tb = ''

				if issubclass(type(e), Base):
					response.returnCode    = e.returnCode
					response.stringContent = e.returnMsg
				else:
					response.returnCode    = 500
					response.stringContent = f'Internal server _error.\n{tb}'

				response.contentType = 'text/plain'
				response.charset     = 'utf-8'

			return response.getContent()

		# No matching route found
		# todo create a Error-Controller
		routeError = Route(
			path='/error',
			httpMethod=HttpMethods.GET,
			nameController='error',
			nameMethod='index'
		)
		
		response = Response(
			startResponse=startResponse,
			request=Request(env=env, route=routeError),
            route=routeError
		)

		response.returnCode    = 404
		response.stringContent = f"No controller method found for route: {env.get('REQUEST_METHOD')}_{env.get('PATH_INFO')}"
		response.contentType   = 'text/plain'
		response.charset       = 'utf-8'

		return response.getContent()


	def __loadConfig(self):
		"""
			Reads the variables from project root config.py
		:return:
		"""
		config = import_module(name=self.__nameConfig)
		for k in dir(config):
			if k.startswith('__'):
				continue

			self._config[k] = getattr(config, k)

		return


	def __loadRoutes(self):
		"""
			Loads and creates all routes from project root routes.py
			and injects the configuration to them.
		:return:
		"""
		module = import_module(name=self.__nameRoutes)
		for route in getattr(module, self.__nameRoutes):
			route.setConfig(config=self._config)
			k = f'{route.httpMethod.name}_{route.pathRegEx}'
			self.__routes[k] = route


	def __addAccessControlHeader(self, request: Request, response: Response):
		"""
			Adds the Access-Control-Allow-Origin header to the response,
			if project root config.py has a key accessControlAllowOrigin,
			holding an list of strings.

		:param request:
		:param response:
		:return:
		"""
		if 'accessControlAllowOrigin' not in self._config:
			return

		accessControlAllowOrigin = []
		accessControlAllowOrigin = accessControlAllowOrigin + self._config['accessControlAllowOrigin']

		if 0 == len(accessControlAllowOrigin) or False == request.hasHeader('Origin'):
			return

		for url in accessControlAllowOrigin:
			if request.getHeader('Origin') == url:
				response.addHeader('Access-Control-Allow-Origin', url)


	def __str__(self):
		"""
			Just a dump string representation of the kernel
			for debugging purposes only.
		"""
		ret = 'Config:\n'
		for k in self._config:
			ret += '\t{key}={val}\n'.format(key=k, val=self._config[k])

		ret += '\nRoutes:\n'

		for k in self.__routes:
			ret += '\t' + str(self.__routes[k]) + '\n'

		ret += '\nENV:\n'

		for k in self.__env:
			ret += '\t{key}={val}\n'.format(key=k, val=self.__env[k])

		return ret
