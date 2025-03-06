from aiohttp import web
import asyncio

queue = asyncio.Queue()
results = []

def factorial(n):
    result = 1
    for i in range(2, n+1):
        result *= i

    return result

async def worker(queue, results):
    while True:
        n= await queue.get()
        if n is None:
            queue.task_done()
            break
        await asyncio.sleep(0.1)

        res = factorial(n)
        results.append(res)
        print(f'Обработано задание: factorial({n}) = {res}')
        queue.task_done()




async def add_task(request):
    try:
        data = await request.json()
        n = data.get('number')
        if n is None:
            return web.json_response({'error': 'Не указан параметр number'}, status=400)
        await queue.put(n)
        return web.json_response({'status': 'Задание добавлено', 'number': str(n)}, status=200)
    
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)
    
async def status(request):
    remaining = queue.qsize()
    return web.json_response({'remaining_tasks': str(remaining)})

async def init_background_workers(app):
    # Создаем N воркеров (например, количество ядер или фиксированное число)
    N = 4
    app['workers'] = [asyncio.create_task(worker(queue, results)) for _ in range(N)]
    # Ждем, пока очередь не опустеет (но это можно делать отдельно)
    # app['worker_group'] = asyncio.gather(*app['workers'])

async def cleanup_background_workers(app):
    # Отправляем сигнал завершения каждому воркеру
    N = len(app['workers'])
    for _ in range(N):
        await queue.put(None)
    # Ждем завершения всех воркеров
    await asyncio.gather(*app['workers'])

app = web.Application()
app.add_routes([
    web.post('/add_task', add_task),
    web.get('/status', status)
])

# Регистрируем функции инициализации и очистки
app.on_startup.append(init_background_workers)
app.on_cleanup.append(cleanup_background_workers)



if __name__ == '__main__':
    web.run_app(app, host="127.0.0.1", port=8080)

