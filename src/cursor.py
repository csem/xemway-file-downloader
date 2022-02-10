from asyncio.log import logger
import math
import json
from typing import List, Union, Literal

FilterLogic = Union[Literal["or"], Literal["and"]]
FilterableValue = Union[str, int, float]


class Filter:

    def __init__(self, field: str, operator: str, value: FilterableValue):
        self._field = field
        self._operator = operator
        self._value = value

    def set_value(self, value: FilterableValue):
        self._value = value

    def serialize(self):
        return {
            "field": self._field,
            "operator": self._operator,
            "value": self._value
        }


class FilterCollection():

    def __init__(self, logic: FilterLogic,
                 filters: List[Union[Filter, 'FilterCollection']]):
        self._logic = logic
        self._filters = filters

    def serialize(self):
        return {
            "logic": self._logic,
            "filters": [f.serialize() for f in self._filters]
        }


OptionalFilterCollection = Union[FilterCollection, None]


class Cursor:

    def __init__(self, base_filtering: OptionalFilterCollection = None):
        """A cursor permitting the iteration over several pages

        Args:
            base_filtering (OptionalFilterCollection, optional): A list of pre-filters given by the instanciator, which couples with an "and" given by the iniator. Defaults to None.
        """
        self._page = -1
        self.num_per_page = 20
        self._base_filtering = base_filtering

    def init(self, filtering: OptionalFilterCollection = None):
        """Initializes the cursor by looking for the first page

        Args:
            filtering (OptionalFilterCollection, optional): A additional collection of filters to refine the filtering. Defaults to None.
        """
        self._filtering = filtering
        self._findById(0)

    def get_count(self):
        """Finds the number of elements matched by the cursor

        Returns:
            int: Total number of elements
        """
        return self._count

    def check_count(self, id):
        logger.debug(f"Id: {id}")
        if id > self._count:
            raise Exception(
                f"Index {id} exceeds the maximum number of documents.")

    def next(self, byHowMany: int = 1):
        """Moves the cursor forward

        Args:
            byHowMany (int, optional): offset used to access the next element in the list. Defaults to 1.

        Returns:
            Cursor: the cursor (self)
        """
        id = self._id + byHowMany

        self.check_count(id)
        self._findById(id)
        return self

    def prev(self, byHowMany: int = 1):
        """Moves the cursor backwards

        Args:
            byHowMany (int, optional): offset used to access the previous element in the list. Defaults to 1.

        Raises:
            Exception: When the index is out of bounds

        Returns:
            Cursor: the cursor (self)
        """
        id = self._id - byHowMany
        if id < 0:
            raise Exception(f"Index f{id} is negative.")
        self._findById(id)
        return self

    def _findById(self, id: int):

        if id == 0:
            page = 1
        else:
            page: int = math.floor(id / self.num_per_page) + 1

        if page != self._page:
            self.fetch(page)

        id_in_page = id - (page - 1) * self.num_per_page
        self.check_count(id)
        self._item = self._items[id_in_page]
        self._id = id

    def get_item(self):
        """Returns the current element matched by the cursor

        Returns:
            any: The current element matched by the cursor
        """
        return self._item

    def fetch(self, page: int):

        filtering = json.dumps({
            "skip": (page - 1) * self.num_per_page,
            "take": self.num_per_page,
            "filter": {
                "logic":
                "and",
                "filters": [
                    f.serialize()
                    for f in filter(lambda f: f is not None,
                                    [self._filtering, self._base_filtering])
                ]
            }
        })

        out = self._fetch(filtering)
        self._items = out["results"]
        #self._num_per_page = out["pagination"]["pageSize"]
        self._count = out["pagination"]["count"]
        self._page = out["pagination"]["page"]

    def _fetch(self):
        raise Exception("Function must be implemented")
