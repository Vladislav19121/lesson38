from aiohttp import web
import asyncio

queue = asyncio.Queue()
exit_prices = []

def order_sum(order_price):
    summa = order_price + 1000 #условно фиксированная цена за доставку
    return summa

async def worker(queue, exit_prices):
    while True:
        order_price = await queue.get()
        if order_price is None:
            queue.task_done()
            break
        await asyncio.sleep(0.1)

        exit_price = order_sum(order_price)
        exit_prices.append(exit_price)
        for index, price in enumerate(exit_prices, start=1):
            print(f'Номер заказа - {index}, eго цена - {price}')
        print(f'Изначальная стоимость заказа - {order_price} руб.\nКонечная стоимость - {exit_price} руб.')
        queue.task_done()

async def add_order(request):
    try:
        data = await request.json()
        order_price = data.get('order_price')
        if order_price is None:
            return web.json_response({'error': 'Не указана цена заказа'}, status=400)
        await queue.put(order_price)
        return web.json_response({'status': f'Добавлена стоимость нового заказа - {order_price}'})

    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

async def get_status(request):
    remaining_orders = queue.qsize()
    return web.json_response({'remaining_orders': str(remaining_orders), 'exit_prices': exit_prices})

async def init_background_workers(app):
    N = 4
    app['workers'] = asyncio.create_task(worker(queue, exit_prices))

async def cleanup_workers(app):
    N = len(app['workers'])
    for i in range(N):
        await queue.put(None)
    await asyncio.gather(*app['workers'])    

app = web.Application()
app.add_routes([
    web.get('/get_status', get_status),
    web.post('/add_order', add_order)
]
)

app.on_startup.append(init_background_workers)
app.on_cleanup.append(cleanup_workers)

if __name__ == '__main__':
    web.run_app(app, host="127.0.0.1", port=8080)