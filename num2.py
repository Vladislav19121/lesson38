from aiohttp import web
import aiohttp_jinja2
import jinja2

app = web.Application()

aiohttp_jinja2.setup(app, loader = jinja2.FileSystemLoader('./templates'))
@aiohttp_jinja2.template('index.html')
async def index (request):
    list_dict = [{"title": "Первый пост", "content": "Содержимое первого поста"}, 
                {"title": "Второй пост", "content": "Содержимое второго поста"},
                {"title": "Третий пост", "content": "Содержимое третьего поста"}]
    return  {'posts': list_dict}

app.add_routes([web.get('/', index)])

web.run_app(app, host='127.0.0.1', port=8080)