import requests, os, asyncio, aiofiles, time
from aiohttp import ClientConnectionError, ClientSession
import imageio
start = time.time()

if os.path.exists('rilla_assets.txt'):
    with open('rilla_assets.txt') as f:
        assets = set(map(int, f.read().split(', ')))
else:
    creators = ['PO4CEJB6IV2P5UACZ3P77KJCITMX2ZIT6RMW4WTX6JQGJYNJS6T5E4V27Q', 'MPRRGD2IXHYNHRMOFD5AE6Y2KK6DL32GKDFIZG7SC6TYO6AKK7CZSSBKTA','2QDW33WUCFKDNEZEZPBF7MCJUOFWOTOPAL64NHHVXUXE5B6L5VKQMPYZXA']
    assets = set()

    for creator in creators:
        url = f'https://algoindexer.algoexplorerapi.io/v2/assets?creator={creator}'
        data = requests.get(url).json()
        while 'next-token' in data:
            for asset in data['assets']:
                assets.add(asset['index'])
            data = requests.get(url+f'&next={data["next-token"]}').json()

    with open('rilla_assets.txt', 'w') as outfile:
        data = str(assets)[1:-1]
        outfile.write(data)


wallet = 'GCDW4TJFIDZZJME4NYUWSQWYGEUDSNSMMEQ4JYH7PM7CRQAUXTJFDDOC2A'
wallet_url = f'https://algoindexer.algoexplorerapi.io/v2/accounts/{wallet}'
wallet_data = requests.get(wallet_url).json()
rillas = set()
for asset in wallet_data['account']['assets']:
    if asset['asset-id'] in assets and asset['amount'] == 1:
        rillas.add(asset['asset-id'])

async def fetch_rilla(wallet, rilla_id, session):
    rand_url = f'https://www.randgallery.com/cdn-cgi/image/height=512,quality=80,format=auto,onerror=redirect/cache/images/{rilla_id}.png?v2'
    file_name = f'{wallet}/{rilla_id}.jpeg'
    try:
        resp = await session.request(method='GET', url =rand_url)
        async for data in resp.content.iter_chunked(1024):
            async with aiofiles.open(file_name, "ba") as f:
                await f.write(data)

    except ClientConnectionError:
        return(url, 404)
    return file_name


async def fetch_all_rillas(wallet, rillas):
    if not os.path.exists(wallet):
        os.mkdir(wallet)
    async with ClientSession() as session:
        tasks = []

        for rilla in rillas:
            tasks.append(
                fetch_rilla(wallet, rilla, session)
            )
        results = await asyncio.gather(*tasks)

    images = []
    for file_name in results:
        images.append(imageio.imread(file_name))
    imageio.mimsave(f'{wallet}.gif', images, duration=.5)

asyncio.run(fetch_all_rillas(wallet, rillas))
print(time.time() - start)