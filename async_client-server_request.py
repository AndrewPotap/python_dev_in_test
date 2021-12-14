import asyncio
import json
from random import randint

id_set = set()


async def handle_echo(reader, writer):
    print("\nOne new connection")
    while True:
        data = await reader.read(800)
        message = data.decode()
        if message == '' or message == '\n':
            writer.close()
            await writer.wait_closed()
            print('Received an empty string', 'Closed the connection', sep=' --->>> ', end='\n\n')
            break
        print('Received from user:', message.rstrip())

        reply_message = json.dumps(parsing_data(message))
        seconds = randint(2, 5)
        print(f"Sent to the client {reply_message.rstrip()} with delay of {seconds} seconds!\n")
        await asyncio.sleep(seconds)
        writer.write(reply_message.encode())
        await writer.drain()


async def main():
    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8889)

    address = server.sockets[0].getsockname()
    print(f'Serving on {address}')

    async with server:
        await server.serve_forever()


def parsing_data(data):
    try:
        received_data = json.loads(data)
        _ = received_data['id'] in id_set
    except:
        return f'Bad client data -- {data.rstrip()}', 'Please try again with correct JSON data!\n'
    else:
        if received_data["id"] not in id_set:
            params = []
            id_set.add(received_data["id"])
            device_data = received_data["data"].split('%%')
            for device_params_set in device_data:
                params.append(device_params_set.split('&&'))
            response = {i[0]: {item: item2 for item, item2 in zip(i[1::2], i[2::2])} for i in params}
            return response
        else:
            return 'Already received these parameters'


if __name__ == "__main__":
    asyncio.run(main())

