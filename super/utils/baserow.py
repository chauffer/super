import os
import aiohttp
class Baserow:
    def __init__(self, key):
        self.key = key
        self.url = 'https://api.baserow.io'
    
    async def api_call(self, path):
        (
            f"{self.url}/{path}",
            headers={
                "Authorization": "Token YOUR_API_KEY"
            }
        )
    async def list_rows(self, args):
