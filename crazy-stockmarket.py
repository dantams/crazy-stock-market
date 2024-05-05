#!/usr/bin/env python

import asyncio
import datetime
import random
import websockets
import json
import decimal

CONNECTIONS = set()

async def register(websocket):
    CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTIONS.remove(websocket)

def random_stock_price() -> decimal.Decimal:
    return decimal.Decimal(random.random() * 1000).quantize(decimal.Decimal('1.00'))

stockmarket = [
    {
        'name': 'AAPL',
        'current': random_stock_price()
    },
    {
        'name': 'GOOG',
        'current': random_stock_price()
    },
    {
        'name': 'TSLA',
        'current': random_stock_price()
    }
]

async def show_tickers():
    while True:
        tickers = { 'datetime': datetime.datetime.now(datetime.UTC).isoformat() }
        tickers['stocks'] = []
        for stock in stockmarket:
            stock['last'] = stock['current']
            stock['current'] = random_stock_price()
            tickers['stocks'].append({
                'symbol' : stock['name'],
                'value': str(stock['current']),
                'change': "{:+}".format(stock['current'] - stock['last'])
            })
        message = json.dumps(tickers, indent=4)
        websockets.broadcast(CONNECTIONS, message)
        await asyncio.sleep(3)

async def main():
    async with websockets.serve(register, "localhost", 5678):
        await show_tickers()

if __name__ == "__main__":
    asyncio.run(main())