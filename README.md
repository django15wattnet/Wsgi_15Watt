# Wsgi-15Watt
A slim, fast and comfortable WSGI-Framework for Python >= 3.6.  
Tested with 3.10 + 3.12.  
Uses https://github.com/defnull/multipart for handling the multipart/form-data requests instead of cgi.FieldStorage.

## Installation
### PIP
```pip3 install Wsgi_15Watt```

### Git
You can clone the [repository](https://github.com/django15wattnet/Wsgi_15Watt) and
install the package to a directory, from where you can import python packages. 
```
    cd /path/to/your/import/able/python/packages
    git clone git@github.com:django15wattnet/15Watt_Wsgi.git
```

## SRC Documentation
[See](https://wsgi.15watt.net)

## Usage

### The Apache2 Configuration
Read the [mod_wsgi docu](https://modwsgi.readthedocs.io/en/master/configuration.html).
```
<VirtualHost x.x.x.x:port>
    ServerName your.server.name
    DocumentRoot /path/to/static/files                          # Where your static html-files are stored
    
    WSGIScriptAlias / /path/to/python/files/application.py      # Where your application.py is stored and invoked by calling http[s]://your.server.name/
    WSGIProcessGroup name_of_your_wsgi_daemon_process           # The name of your WSGIDaemonProcess
    
    # For development, each request loads a new python interpreter / application.py, no need the reload the web server
    WSGIDaemonProcess name_of_your_wsgi_daemon_process user=yourUnixUser group=yourUnixGroup processes=1 threads=1 maximum-requests=1 home=/path/to/python/files python-path=/path/to/python/files
    
    # For a production enviroment change processes, threads and maximum-requests to your needes
    
    # The confiuration for the static files
    <Directory /path/to/static/files/>
    # Read the Apache2 docu https://httpd.apache.org/docs/2.4/mod/core.html#directory
       Options -Indexes -FollowSymLinks -MultiViews -Includes
       AllowOverride None
       Require all granted
       allow from all
    </Directory>
    
    # The configuration for the application directory
    <Directory /path/to/python/files/>
    # Read the Apache2 docu https://httpd.apache.org/docs/2.4/mod/core.html#directory
        Require all granted
        Options FollowSymLinks
        AllowOverride None
        Header set Access-Control-Allow-Origin '*'          # I'm not sure if this is needed
    </Directory>
    
    # Alias for the static, directly by the web server, deliveryed files and directories
    Alias /favicon.ico /path/to/static/files/favicon.ico
    Alias /css/ /path/to/static/files/css/
    Alias /js/ /path/to/static/files/js/
    Alias /img/ /path/to/static/files/img/ 
    
    ...
    
    # Your other Apache configurations
    
    </VirtualHost>
```

### Project Layout
@ToDo

### The Application
Create a ```application.py``` file in ```/path/to/python/files```:
```  
#!/usr/bin/env python
from Wsgi-15Watt.Kernel import Kernel

kernel = None

def application(env: dict, start_response):
	global kernel

	if kernel is None:
		kernel = Kernel()

	return kernel.run(env=env, startResponse=start_response)
```
All requests are handled by the Kernel.run method.  ```WSGIScriptAlias / /path/to/python/files/application.py```  
The Kernel is a singleton and is created only once per lifetime of the application. By this, the configuration und the routes are loaded only once.  
**Only files and/or directories definded by Apache Alias directives are delivered by the web server drircetly!**

### Routes
The routes definitions tells the Kernel witch request path ist mapped to witch controller and method.  
Create a ```routes.py``` file in ```/path/to/python/files```:

#### Example routes without parameters in the path
```
from Wsgi-15Watt.Route import Route, HttpMethods

routes = [
	Route(
		path='/',
		nameController='Controllers.AggregationController.AggregationController',
		nameMethod='staticPageAction',
		httpMethod=HttpMethods.GET
	),
	Route(
		path='/qcell',
		nameController='QCell.StaticPagesController.StaticPagesController',
		nameMethod='indexAction',
		httpMethod=HttpMethods.GET
	),
]
```
A request to ```/``` will be handled by ```from Controllers.AggregationController import AggregationController```  ```staticPageAction``` method.  
A request to ```/qcell``` will be handled by ```from QCell.StaticPagesController import StaticPagesController```  ```indexAction``` method.

#### Example routes with parameters in the path
```
from Wsgi-15Watt.Route import Route, HttpMethods

routes = [
	Route(
		path='/do/{id}/{what}',
		nameController='Controllers.DoWiredStuffController.DoWiredStuffController',
		nameMethod='doStuffAction',
		httpMethod=HttpMethods.GET,
		params = {
                    'id': 'int',
                    'what': 'str'
                }
	),
    ...
]
```
A request to ```/do/42/machWas``` will be handled by 
```from Controllers.DoWiredStuffController import DoWiredStuffController```  
```doStuffAction``` method with the parameters ```id=42``` and ```what='machWas'```.  
The types of the parameters in the path can be python types ``ìnt`` or ```str```.

#### Route names
Routes have names.  
They are build automatically, or set throw the parameter
```name``` in the Route constructor.
The automatically build name of a route is build by the name of the controller 
and the name of the method.

```def nameMatches(self, lstNames: list|str = []) -> bool:```  \
The method ```nameMatches``` of the Route class checks if the name of the route 
matches one of the names in the list ```lstNames```.

### The Request Class
represents the request from the client.  
Have a look at the, hopefully, well documented code.

### The Response Class
represents the response send to the client.  
Have a look at the, hopefully, well documented code.

### Controllers
The controllers orchestrate the work to be done. Receive the request, do the work and return the response.

#### A very simple example Controller
```
from Wsgi-15Watt.BaseController import BaseController
from Wsgi-15Watt.Request import Request
from Wsgi-15Watt.Response import Response


class ExampleController(BaseController):

	def __init__(self, config: dict):
		super().__init__(config=config)


	def getAction(self, request: Request, response: Response):
		response.stringContent = 'Hello World'
		response.contentType = 'text/plain
		response.returnCode = 200
		return
```
Will send the string 'Hello World' with the content type 'text/plain' and the return code 200 to the client.  
Do what ever you want in your getAction method 😊.


#### A controller with a method that gets parameters from the route
The route with parameters in the path ```/path/to/python/files/routes.py```:
```
from Wsgi-15Watt.Route import Route, HttpMethods

routes = [
	Route(
		path='/with/params/{id}/{what}',
		nameController='Controllers.ExampleController.ExampleController',
		nameMethod='withParamsAction',
		httpMethod=HttpMethods.GET,
		params = {
                    'id': 'int',
                    'what': 'str'
                }
	)
]
```
The controller ```/path/to/python/files/Controllers/ExampleController.py```:
```
from Wsgi-15Watt.BaseController import BaseController
from Wsgi-15Watt.Request import Request
from Wsgi-15Watt.Response import Response


class ExampleController(BaseController):

	def __init__(self, config: dict):
		super().__init__(config=config)


	def withParamsAction(self, request: Request, response: Response):
		response.stringContent = f'Hello World, id = {request.get('id)} what = "{request.get('what')"}'
		response.contentType = 'text/plain
		response.returnCode = 200
		return
```
When the client requests ```/with/params/42/machWas```  
the response will be ```Hello World, id = 42 what = "machWas"```  
with the content type 'text/plain' and the return code 200.

```request.get('id)``` will return the value of the parameter ```id``` as type int from the request.  
```request.get('what)``` will return the value of the parameter ```what``` as type str from the request.


### The configuration file
is expected in ```/path/to/python/files/config.py```  
as a simple assignments of variables to values.  
```
key1 = 'Value1'
confVar2 = 42
```
The Kernel will load the configuration file and make the variables, as a dict, available to the controllers,  
in the property ```'self._config```  
whit this content:
```
{
    'key1': 'Value1', 
    'confVar2': 42
}
```

## Templates
I use [Cheetah3](https://cheetahtemplate.org/) for the templates.  
Use what ever you like as your template engine.  
At this moment (2024-06-01) I'm not shure the BaseTplController is necessary.  
If you like to use Cheetah3, have a look at the [WsgiCheetah3_15Watt](https://github.com/django15wattnet/WsgiCheetah3_15Watt) extension.

## How to create the documentation
The documentation is generated by [pdoc](https://pdoc.dev/).
cd into the directory above the Wsgi_15Watt directory and run:
```
PYTHONPATH=. python3 -m pdoc -o Wsgi_15Watt/docs Wsgi_15Watt
```

## Extensions
- [WsgiCheetah3_15Watt](https://github.com/django15wattnet/WsgiCheetah3_15Watt): An extension to use Cheetah3 templates comfortable.
- [WsgiSqlObject_15Watt](https://github.com/django15wattnet/WsgiSqlObject_15Watt): Adds SQLObject support to Wsgi_15Watt.

## ToDos
- Find a way to determine that a uri (with parameters) matches a route
  - vulgo: find a way to determine that the request path ```/do/42/machWas``` matches the route ```/do/{id}/{what}```
- Change the language of the comments and documentation from german to english
- Write and test a configuration for [nginx](https://nginx.org/)
