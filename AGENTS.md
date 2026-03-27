# AGENTS Guide for Wsgi_15Watt

## Big Picture (Request -> Response)
- `Kernel.run()` in `Kernel.py` is the runtime entrypoint: it finds the first matching route, builds `Request`/`Response`, calls controller action, then returns `response.getContent()`.
- Route matching is strict on method + regex path (`Route.match()` in `Route.py`), with trailing slash normalization (`/foo/` -> `/foo`).
- Controllers are loaded dynamically from route strings like `Controllers.X.YController` (`Route.__buildMethod()`), instantiated with `config` from `config.py`.
- If no route matches, framework returns plain-text 404 in `Kernel.run()`.
- Exceptions deriving from `Exceptions.Base` are translated to HTTP code/message in `Kernel.run()`; other exceptions become 500 (with traceback only when `debug=True` in config).

## Configuration + Routing Contracts
- `Kernel` imports project-root modules by name (`config`, `routes` by default), so these modules must be importable in `PYTHONPATH`.
- In `routes.py`, export a list named exactly like the module name (`routes`), because `Kernel.__loadRoutes()` calls `getattr(module, self.__nameRoutes)`.
- Route path parameters must be declared in `paramsDef` and support only `'int'` or `'str'` (`Route.__buildPathRegEx()`).
- Use `nameRoute` only if you need a stable custom route name; default is built from controller + method + HTTP method.

## Request/Response Data Flow Details
- `Request` merges params from three sources (path params, query string, multipart/form body) in `Request.__getParameters()`.
- For repeated keys, values are accumulated as lists; `Request.get()` returns the first value, `Request.getAsList()` returns all.
- File uploads are parsed via vendored `multipart.py` (`parse_form_data`) and exposed by `Request.getFile()` / `hasFile()`.
- `Response.getContent()` always calls WSGI `start_response` and returns `list[bytes]`; controller actions should mutate `response` instead of returning body strings.
- `Response.__buildHeader()` always sets `Content-type` and default `Access-Control-Allow-Origin: *`; `Kernel` may add another origin header if configured.

## Project-Specific Patterns for Controllers
- Controller action signature is `action(self, request: Request, response: Response)`; mutate `response.stringContent` or `response.byteContent`.
- Base class is `BaseController` and receives injected config as `self._config`.
- For BasicAuth-gated actions, use `decoratorLoginRequired` from `BaseController.py` (expects `AUTH_TYPE=Basic` and `REMOTE_USER`).
- `BaseTplController` expects `pathBase` and `pathTemplates` in config and reads template files directly.

## Dependencies + Integration Points
- Core external dependency: `SQLObject~=3.11.0` (`requirements.txt`), used in `Kernel.__connectToDatabase()` when `uriDb` exists in config.
- Multipart handling is intentionally not `cgi.FieldStorage`; project uses local `multipart.py` (from defnull/multipart).
- Deployment assumptions are Apache + `mod_wsgi` (`README.md`); static assets are expected to be served by Apache aliases, not by this framework.

## Developer Workflow (Current Repo Reality)
- No automated test suite is present in this repository; validate changes with focused local smoke tests.
- Package build flow is script-driven: `makePyPiPackage.sh` creates `pypiPackage/` and runs `python3 -m build`.
- Generated docs exist under `docs/`; treat them as generated artifacts unless you intentionally regenerate documentation.

## Sharp Edges to Respect
- In `Exceptions.py`, subclasses currently set private fields without calling `Base.__init__`; if you add/modify exceptions, ensure `.returnCode` / `.returnMsg` still work with `Kernel` error mapping.
- `Request` reads `wsgi.input` during initialization; middleware/controllers should not expect unread request body streams afterward.
- Keep route/controller wiring explicit; dynamic import strings are fragile to module renames.

