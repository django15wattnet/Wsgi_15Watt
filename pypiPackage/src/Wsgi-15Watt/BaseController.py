from .Request import Request
from .Response import Response
from .Route import Route
from .Exceptions import Unauthorized


def decoratorLoginRequired(func):
	"""
		A decorator for controller methods, that checks if the user has logged in via BasicAuth.

		If not so, a 401 Unauthorized exception is raised.
	"""
	def wrapper(self, request: Request, response: Response):
		if 'Basic' != request.getEnvByKey('AUTH_TYPE'):
			# Send a 401 response as plain/text, not a exception/500er
			raise Unauthorized(
				returnCode=401,
				returnMsg=f"Invalid auth type: {request.getEnvByKey('AUTH_TYPE')}"
			)

		if request.getEnvByKey('REMOTE_USER') is None:
			raise Unauthorized(returnCode=401, returnMsg='Unauthorized')

		return func(self, request, response)
	return wrapper


class BaseController(object):
	"""
		Basisklasse of all controllers.
	"""
	def __init__(self, config: dict):
		self._config = config
