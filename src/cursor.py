
import math


class Cursor:

    def __init__(self):
        self._page = -1

    def init(self):
        self._findById(0)

    def get_count(self):
        return self._count

    def current(self):
        return self._curent

    def next(self, byHowMany: int = 1):
        id = self._id + byHowMany
        if id >= self._count:
            raise Exception(
                f"Index f{id} exceeds the maximum number of documents.")
        self._findById(id)
        return self

    def prev(self, byHowMany: int = 1):
        id = self._id - byHowMany
        if id < 0:
            raise Exception(f"Index f{id} is negative.")
        self._findById(id)
        return self

    def _findById(self, id: int):
        if id == 0:
            page = 1
        else:
            page: int = math.floor(id / self._num_per_page) + 1

        if page != self._page:
            self.fetch(page)

        id_in_page = id - (page - 1) * self._num_per_page
        self._item = self._items[id_in_page]
        self._id = id

    def get_item(self):
        return self._item

    def fetch(self, page: int):
        out = self._fetch(page)

        self._items = out["results"]
        self._num_per_page = out["pagination"]["pageSize"]
        self._count = out["pagination"]["count"]
        self._page = out["pagination"]["page"]

    def _fetch(self):
        raise Exception("Function must be implemented")
