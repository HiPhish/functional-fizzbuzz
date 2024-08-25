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
from itertools import pairwise
from string import ascii_letters
from hypothesis import given, strategies as st
from .fizzbuzz import Rule, compile_rules


def unambiguous_rule_names(rules: list[Rule]):
    """None of rule texts contain another rule's text."""
    texts = {rule.value for rule in rules}
    return all(
        not any(text2.startswith(text) for text2 in (texts - {text}))
        for text in texts
    )


@st.composite
def rules(draw) -> Rule:
    """
    Returns a strategy which randomly generates FizzBuzz rules.

    :return: Rule with random number and string value
    """
    number = draw(st.integers(min_value=2))
    value = draw(st.text(ascii_letters, min_size=1)).title()
    return Rule(number, value)


@st.composite
def rulesets(draw, max_size=5) -> Rule:
    """
    Returns a strategy which generates a random FizzBuzz rule set.  All rules
    have unique number and value.  Additionally the value of one rule is
    guaranteed to never be part of another rule's value.  This ensures that
    there is an unambiguous mapping between the output string and the rules
    which produced it.

    :param max_size: Maximum number of rules in the rule set
    :return: Unambiguous ruleset of random rules
    """
    ruleset = draw(st.lists(rules(), min_size=1, max_size=max_size,
                            unique_by=(lambda r: r.value, lambda r: r.number))
                   .filter(unambiguous_rule_names))
    return ruleset


@given(rules(), st.integers(min_value=1))
def test_rule_success(rule: Rule, n: int):
    """Rule applies to numbers which are multiple of the rule's number."""
    assert rule.test(n * rule.number)


@given(rules(), st.integers(min_value=0), st.data())
def test_rule_failure(rule: Rule, n: int, data: st.DataObject):
    """
    Rule does not apply to numbers which are not multiple of the rule's number.
    """
    i = data.draw(st.integers(min_value=1, max_value=rule.number - 1),
                  label='remainder')
    assert not rule.test(n * rule.number + i)


@given(rulesets(), st.integers(min_value=1))
def test_fizzbuzz_contains_value(rules: list[Rule], n: int):
    """
    The output of the program is either the number itself if none of the rules
    apply, or the concatenation of all values of the rules which apply in the
    order the rules were given.
    """
    program = compile_rules(rules)
    expected = ''.join(rule.value for rule in rules if rule.test(n))
    result = program(n)
    match expected:
        case '':
            assert result == str(n)
        case _:
            assert result == expected


@given(st.iterables(rules(), min_size=1, max_size=5, unique=True),
       st.integers(min_value=1),
       st.integers(min_value=2, max_value=1000))
def test_fizzbuzz_idempotent(rules: list[Rule], n: int, times: int):
    """
    Running the program multiple times produces the same result even when the
    rule set is an exhaustible generator.
    """
    program = compile_rules(rules)
    outputs = [program(n) for _ in range(times)]
    assert all(outputs[0] == output for output in outputs)


# Here is an alternative test which does not re-implement the compiler
@given(rulesets(), st.data())
def test_fizzbuzz_number(rules: list[Rule], data: st.DataObject):
    """A number which not divisible by any rule is printed as is."""
    n = data.draw(st.integers()
                    .filter(lambda n: not any(r.test(n) for r in rules)),
                  label='number')
    program = compile_rules(rules)
    assert program(n) == str(n)


@given(rulesets(), st.data())
def test_fizzbuzz_contains_match(rules: list[Rule], data: st.DataObject):
    """If the number is divisible the result contains the rule's text."""
    n = data.draw(st.integers()
                    .filter(lambda n: any(r.test(n) for r in rules)),
                  label='number')
    positives = [r for r in rules if r.test(n)]
    program = compile_rules(rules)
    result = program(n)
    present = [r for r in rules if r.value in result]
    assert positives == present


@given(rulesets(), st.data())
def test_fizzbuzz_contains_no_mismatch(rules: list[Rule], data: st.DataObject):
    """
    If the number is not divisible the result does not contain the rule's text
    """
    n = data.draw(st.integers()
                    .filter(lambda n: any(r.test(n) for r in rules)),
                  label='number')
    negatives = [r for r in rules if not r.test(n)]
    program = compile_rules(rules)
    result = program(n)
    absent = [r for r in rules if r.value not in result]
    assert negatives == absent


@given(rulesets(), st.data())
def test_fizzubzz_results_order(rules: list[Rule], data: st.DataObject):
    """The rule values are in the same order they were given in."""
    n = data.draw(st.integers().filter(lambda n: any(r.test(n) for r in rules)))
    positives = (r for r in rules if r.test(n))
    program = compile_rules(rules)
    result = program(n)
    positions = (result.find(r.value) for r in positives)
    assert all(a < b for a, b in pairwise(positions))
