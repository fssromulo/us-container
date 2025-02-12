# Python imports
import re
from typing import Any


def extract_integers_from_string(input_string) -> list[int]:
    integers_list: list[Any] = re.findall(pattern=r'\d+', string=input_string)
    integers = list(map(int, integers_list))
    return integers
