import asyncio
import json

DATA = {"id": "01", "data": "Hub&&name&&var1&&value&&123%%Device&&name&&var2&&value&&132"}


async def tcp_echo_client(client_object):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8889)
    client_data = json.dumps(client_object)
    writer.write(client_data.encode())
    await writer.drain()
    print('Sent to the server', client_data)

    received_data = await reader.read(800)
    message = received_data.decode()
    print(f'Received: {message}')

asyncio.run(tcp_echo_client(DATA))
