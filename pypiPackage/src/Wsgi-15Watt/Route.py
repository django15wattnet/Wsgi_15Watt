from enum import Enum
from importlib import import_module
import re
from .Exceptions import NotAllowedHttpMethod, InvalidData


class HttpMethods(Enum):
    """
        Die erlaubten HTTP-Methoden
    """
    GET      = 1
    POST     = 2
    PUT      = 3
    PATCH    = 4
    DELETE   = 5
    COPY     = 6
    HEAD     = 7
    OPTIONS  = 8
    LINK     = 9
    UNLINK   = 10
    PURGE    = 11
    LOCK     = 12
    PROPFIND = 13
    VIEW     = 14


class Route(object):
    """
    The route is the connection between the path and the called controller method.

    Example:

        Route(
            path='/adm/image/edit/{id}',
            nameController='image.AdmController.AdmController',
            nameMethod='admEditAction',
            httpMethod=HttpMethods.POST,
            paramsDef={
                'id': 'int',
                'description': 'str'
            },
            nameRoute='admImageList'
        )

    """
    def __init__(
            self,
            path: str,
            nameController: str,
            nameMethod: str,
            httpMethod: HttpMethods,
            paramsDef: dict = None,
            nameRoute: str|None = None
    ):

        if httpMethod not in HttpMethods:
            raise NotAllowedHttpMethod(returnMsg=httpMethod.name)

        self.__path                = path
        self.__nameControllerParts = nameController.split('.')
        self.__nameMethod          = nameMethod
        self.__methodToCall        = None
        self.__httpMethod          = httpMethod
        self.__dictParamsDef       = paramsDef
        self.__nameRoute           = self.__buildNameRoute(nameRoute)
        self.__pathRegEx           = self.__buildPathRegEx()

        if paramsDef is None:
            self.__dictParamsDef = {}
        else:
            self.__config = paramsDef


    @property
    def path(self) -> str:
        """
        Returns the path defined in the route.
        """
        return self.__path


    @property
    def methodToCall(self):
        """
        Returns the method to call.
        """
        if self.__methodToCall is None:
            self.__methodToCall = self.__buildMethod()

        return self.__methodToCall


    @property
    def httpMethod(self) -> HttpMethods:
        """
        Returns the HTTP-method
        """
        return self.__httpMethod


    @property
    def pathRegEx(self) -> str:
        """
        Returns the RegEx-String to match the route
        """
        return self.__pathRegEx
    
    
    @property
    def name(self) -> str:
        """
        Returns the name of the route, if defined. Otherwise, returns an empty string.
        """
        return self.__nameRoute


    def setConfig(self, config: dict):
        """
        Set the configuration from project root config.py for the route
        """
        self.__config = config


    def match(self, path: str, httpMethod: HttpMethods) -> bool:
        """
        Checks if the route matches path and httpMethod
        """
        if httpMethod != self.__httpMethod:
            return False

        path = path.rstrip('/')
        if '' == path:
            path = '/'
        
        return re.match(f'^{self.__pathRegEx}$', path) is not None


    def getParamsFromPath(self, path: str) -> dict:
        """
            Returns the parameters from the path
        """
        matches = re.match(self.__pathRegEx, path)
        if matches is None:
            return {}

        paramsFromPath = {}
        for placeHolder in self.__dictParamsDef:
            if 'str' == self.__dictParamsDef[placeHolder]:
                paramsFromPath[placeHolder] = matches.group(placeHolder)
            elif 'int' == self.__dictParamsDef[placeHolder]:
                paramsFromPath[placeHolder] = int(matches.group(placeHolder))

        return paramsFromPath
    
    
    def nameMatches(self, lstNames: list|str = []) -> bool:
        if type(lstNames) is str:
            lstNames = [lstNames]
            
        return self.__nameRoute in lstNames
    


    def __buildMethod(self):
        """
        Build the callable method, that will be call for the route
        """
        nameModule = '.'.join(self.__nameControllerParts[:-1])
        nameClass  = self.__nameControllerParts[-1]
        module     = import_module(name=nameModule)
        inst       = getattr(module, nameClass)(config=self.__config)

        return getattr(inst, self.__nameMethod)


    def __buildPathRegEx(self):
        """
        Build the RegEx-String to match the route
        """
        strPathRegEx = self.__path

        for placeHolder in re.findall(r'\{[\w]{1,}\}', strPathRegEx):
            placeHolderPlain = placeHolder.strip('{}')

            if placeHolderPlain not in self.__dictParamsDef:
                raise InvalidData(returnMsg=f'Parameter "{placeHolderPlain}" not defined in paramsDef. Route = {self.__path}')

            if 'str' == self.__dictParamsDef[placeHolderPlain]:
                to = r"(?P<{n}>[\w\/\-\.]{{1,}})".format(n=placeHolderPlain)
            elif 'int' == self.__dictParamsDef[placeHolderPlain]:
                to = "(?P<{n}>[0-9]{{1,}})".format(n=placeHolderPlain)
            else:
                raise InvalidData(returnMsg=f'Not allowed data type: {self.__dictParamsDef[placeHolderPlain]}')

            strPathRegEx = strPathRegEx.replace(placeHolder, to)
        return strPathRegEx
    
    
    def __buildNameRoute(self, nameRoute: str|None) -> str:
        """
        Builds the name of the route. If nameRoute is not empty, it is returned.
        Otherwise, the name is built from the controller, the method to call,
        and the httpMethod.
        """
        if nameRoute is not None:
            return nameRoute
        
        return ('.'.join(self.__nameControllerParts)
                + ':'
                + self.__nameMethod
                + ':'
                + self.__httpMethod.name)


    def __str__(self):
        return f'Route - Path={self.__path} {self.__httpMethod.name} {".".join(self.__nameControllerParts)}.{self.__nameMethod}'
