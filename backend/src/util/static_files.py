import stat

import anyio
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope


class ReactStaticFiles(StaticFiles):
    """
    Wrapper around StaticFiles that supports client side routing in react.

    Performs the same as the `try_files` nginx directive. Namely instead of returning 404 for an unkown path, we
        return `index.html` and let react handle the routing / 404. This allows users to refresh / load paths defined
        in the react app
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except HTTPException as e:
            if e.status_code == 404:
                # no file exists here so return index.html instead
                full_path, stat_result = await anyio.to_thread.run_sync(
                    self.lookup_path, "index.html"
                )
                if stat_result is not None and stat.S_ISREG(stat_result.st_mode):
                    return self.file_response(full_path, stat_result, scope)

            raise
