import asyncio, sys
from clicker import *


async def main():
    await keyboard_detector()   
    await coords_finder(0.01)
    
asyncio.run(main())