from a_core.http import get_api_results
from .cache import USER_TTL, cache_api_response
from typing import Literal


class KeeplistAPI:    
    @cache_api_response("user", USER_TTL)
    async def get_user(self, user_id: str):
        if user_id is None:
            raise ValueError("user_id is required")
        return await self._get(f'user/{user_id}')
    
    list_type = Literal['keeps', 'lists']

    @cache_api_response("lists")
    async def get_user_lists(self, user_id: str, list_type: list_type  | None, nested: bool = True):
        if user_id is None:
            raise ValueError("user_id is required")
        params = {'non_nested': True} if not nested else {}
        return await self._get(f'user/{user_id}/a/{list_type}', params)
    
    @cache_api_response("items")
    async def get_items(self, user_id: str, list_type: list_type | None):
        if user_id is None:
            raise ValueError("user_id is required")
        return await self._get(f'user/{user_id}/i/{list_type}')
    
    @cache_api_response("list")
    async def get_list(self, user_id: str, list_type: list_type, list_id: str, nested: bool = True):
        if user_id is None:
            raise ValueError("user_id is required")
        if list_type is None:
            raise ValueError("list_type is required")
        if list_id is None:
            raise ValueError("list_id is required")
        params = {'non_nested': True} if not nested else {}
        return await self._get(f'user/{user_id}/a/{list_type}/{list_id}', params)

    @cache_api_response("items")
    async def get_list_items(self, user_id: str, list_type: list_type, list_id: str):
        if user_id is None:
            raise ValueError("user_id is required")
        if list_type is None:
            raise ValueError("list_type is required")
        if list_id is None:
            raise ValueError("list_id is required")
        return await self._get(f'user/{user_id}/a/{list_type}/{list_id}/items')
    
    @cache_api_response("item")
    async def get_list_item(self, user_id: str, list_type: list_type, list_id: str, item_id: str):
        if user_id is None:
            raise ValueError("user_id is required")
        if list_type is None:
            raise ValueError("list_type is required")
        if list_id is None:
            raise ValueError("list_id is required")
        if item_id is None:
            raise ValueError("item_id is required")
        return await self._get(f'user/{user_id}/a/{list_type}/{list_id}/items/{item_id}')
    
    async def _get(self, endpoint: str, params: dict = None):
        print('api', endpoint, params)
        return await get_api_results(endpoint, params)
    

