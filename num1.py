from aiohttp import web
import json

async def index(request):
    return web.Response(text='Hello, world')

async def greet(request):
    name = request.rel_url.query.get('name', 'Vlad')
    return web.Response(text=f'Hello, {name}!')

async def echo(request):
    try:
        payload = await request.json()
        message = payload.get('message', 'None')
        return web.Response(text=str(message))

    except Exception as e:
        return web.json_response({'status': 'error',
                                  'reason': str(e)},
                                  status=400)

app = web.Application()

app.add_routes([web.get('/', index), web.get('/greet', greet), web.post('/echo', echo)])



web.run_app(app, host='127.0.0.1', port=8080)
