# SPDX-License-Identifier: Unlicense
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or distribute
# this software, either in source code form or as a compiled binary, for any
# purpose, commercial or non-commercial, and by any means.
#
# In jurisdictions that recognize copyright laws, the author or authors of this
# software dedicate any and all copyright interest in the software to the
# public domain. We make this dedication for the benefit of the public at large
# and to the detriment of our heirs and successors. We intend this dedication
# to be an overt act of relinquishment in perpetuity of all present and future
# rights to this software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <https://unlicense.org/>
from typing import Callable, Iterable, NamedTuple
from functools import partial
from itertools import islice, count


class Rule(NamedTuple):
    """
    A single rule of the FizzBuzz game.

    Attributes:
    `number`  The rule applies to an integer `i` if it is divisible by this
    `value`   Text which will be part of the output if the rule applies
    """
    number: int
    value: str

    def __str__(self) -> str:
        """A rule is implicitly represented by its value."""
        return self.value

    def test(self, i: int) -> bool:
        """Test whether this rule applies to the given number `i`."""
        return i % self.number == 0


def compile_rules(rules: Iterable[Rule]) -> Callable[[int], str]:
    """
    Compiles a rule set into an executable FizzBuzzing function.

    :param rules: Ordered sequence of FizzBuzz rules.
    :return: Function which applied to an integer returns the FizzBuzz result
    """
    rules = list(rules)

    def closure(i: int) -> str:
        # Use a map to apply each rule in succession to the number, filter out
        # indivisible ones.  If the result is empty return the number,
        # otherwise join all the strings.
        s = ''.join(map(str, filter(partial(Rule.test, i=i), rules)))
        match s:
            case '':
                return str(i)
            case _:
                return s

    return closure


if __name__ == '__main__':
    rules = [Rule(3, 'Fizz'), Rule(5, 'Buzz')]
    fizzbuzz = compile_rules(rules)
    for line in islice(map(fizzbuzz, count(1)), 100):
        print(line)
