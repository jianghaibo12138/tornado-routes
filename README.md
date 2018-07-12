Tornado routes
==============

URL routings for tornado web server.

Usage examples:

```python
from tornado import web
from tornado_routes import Handlers, include


URL_PREFIX = ''

urls = [
    (r'/user', include('api.user.UserController'))
]

handle = Handlers(url_prefix, urls)

def make_app():
    return web.Application(handlers=handle.make_handlers())

if __name__ == '__main__':
    make_app().listen(8888)
    print("Server starts on the port {}".format(8888))
    ioloop.IOLoop.current().start()
```

`api.py`:

```python
from tornado import web
from tornado_routes import route

@route('foo')
class FooHandler(web.RequestHandler):
    pass
```

`views.py`:

```python
from tornado import web
from tornado_routes import route

@route('', name='index')
class IndexHandler(web.RequestHandler):
    pass
```

Your could use view names in your templates:

```html
<a href="{{ reverse_url('index') }}">Index</a>
<a href="{{ reverse_url('api.FooHandler') }}">Foo link</a>
```
