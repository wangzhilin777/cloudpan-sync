from __future__ import annotations

import uvicorn

from .config import HOST, PORT
from .webapp import create_app


def main() -> None:
    uvicorn.run(create_app(), host=HOST, port=PORT)


if __name__ == "__main__":
    main()
