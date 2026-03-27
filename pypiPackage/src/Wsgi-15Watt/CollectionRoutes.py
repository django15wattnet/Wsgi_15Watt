from typing import Dict

from .Route import Route

class CollectionRoutes(Dict[str, Route]):
	"""
		A dict of routes, where the key is the path of the route.
	"""
	def __init__(self, routes: list):
		super().__init__()

		for route in routes:
			self[route.path] = route