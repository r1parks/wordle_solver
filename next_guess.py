#!/usr/bin/env python3

import random
import string
import sys


HINT_CACHE = {}


def get_hint(guess, target):
    global HINT_CACHE
    key = f'{guess}-{target}'
    if key not in HINT_CACHE:
        hint = ['.'] * 5
        target_letters_remaining = list(target)
        for n, (c1, c2) in enumerate(zip(guess, target)):
            if c1 == c2:
                hint[n] = 'G'
                target_letters_remaining.remove(c2)
        for n, c in enumerate(guess):
            if hint[n] == 'G':
                continue
            if c in target_letters_remaining:
                hint[n] = 'Y'
                target_letters_remaining.remove(c)
        HINT_CACHE[key] = ''.join(hint)
    return HINT_CACHE[key]


def valid_wordle_word(word):
    if len(word) != 5:
        return False
    valid_letters = set(string.ascii_lowercase)
    invalid_letters = set(word) - valid_letters
    if invalid_letters:
        return False
    return True


def build_guess_hint_dict(all_words, words_remaining):
    guess_hint_dict = {}
    for guess in all_words:
        for target in words_remaining:
            hint = get_hint(guess, target)
            guess_hint_dict[guess] = guess_hint_dict.get(guess, {})
            guess_hint_dict[guess][hint] = guess_hint_dict[guess].get(hint, set())
            guess_hint_dict[guess][hint].add(target)
    return guess_hint_dict


def print_guess_hint_dict(guess_hint_dict):
    for guess in guess_hint_dict:
        for hint in guess_hint_dict[guess]:
            print(f'{guess} - {hint} - {len(guess_hint_dict[guess][hint])} words')
            print(guess_hint_dict[guess][hint])


def analyze_guesses(guess_hint_dict):
    result = []
    for guess in guess_hint_dict:
        remaining_per_hint = [len(guess_hint_dict[guess][hint]) for hint in guess_hint_dict[guess]]
        ev = sum(remaining_per_hint) / len(remaining_per_hint)
        maximum = max(remaining_per_hint)
        result.append((guess, ev, maximum))
    return result


def print_analysis(words_with_analysis, title):
    print(f'\n{title}')
    for word, ev, maximum in words_with_analysis:
        print(f'{word} {ev:.1f} expected {maximum} max')


def find_best_guess(all_words, words_remaining):
    guess_hint_dict = build_guess_hint_dict(all_words, words_remaining)
    guess_analysis = analyze_guesses(guess_hint_dict)
    by_ev = sorted(guess_analysis, key=lambda item: (item[1], item[2]))[:10]
    by_max = sorted(guess_analysis, key=lambda item: (item[2], item[1]))[:10]
    only_words_remaining_analysis = [analysis for analysis in guess_analysis if analysis[0] in words_remaining]
    words_remaining_by_ev = sorted(only_words_remaining_analysis, key=lambda item: (item[1], item[2]))[:10]
    words_remaining_by_max = sorted(only_words_remaining_analysis, key=lambda item: (item[2], item[1]))[:10]
    print_analysis(by_ev, 'Best EV')
    print_analysis(by_max, 'Best Max')
    print_analysis(words_remaining_by_ev, 'Best EV Valid Guess')
    print_analysis(words_remaining_by_max, 'Best Max Valid Guess')


def test_get_hint(verbose=False):
    test_cases = [['abcde', 'abcde', 'GGGGG'],
                  ['abcde', 'fghij', '.....'],
                  ['acccc', 'xxxxa', 'Y....'],
                  ['eagle', 'edges', 'G.G.Y'],
                  ['eeaaa', 'aaeee', 'YYYY.'],
                  ['eeeaa', 'aaeee', 'YYGYY'],
                  ['abcde', 'bcdea', 'YYYYY']]
    for guess, target, hint in test_cases:
        actual = get_hint(guess, target)
        if verbose:
            print(f'({guess}, {target}), expected {hint} got {actual}')
        assert actual == hint, f'{guess} - {target} expected {hint} got {actual}'
    if verbose:
        print("tests pass")


def test_valid_wordle_word(verbose=False):
    valid_words = ['abcde', 'aaaaa', 'kdiem', 'iuuud']
    invalid_words = ['abc', 'abcd', '', 'abcdef', 'abcd1', 'abc,d']
    for word in valid_words:
        result = valid_wordle_word(word)
        output = f'"{word}" expects True got {result}'
        assert result, output
        if verbose:
            print(output)
    for word in invalid_words:
        result = valid_wordle_word(word)
        output = f'"{word}" expects False got {result}'
        assert not result, output
        if verbose:
            print(output)


def test(verbose=False):
    test_get_hint(verbose)
    test_valid_wordle_word(verbose)
    if verbose:
        print("all tests pass!")


def main():
    test()
    words_remaining = sys.stdin.read().splitlines()
    words_remaining = set(word for word in words_remaining if valid_wordle_word(word))
    with open('/usr/share/dict/words', 'r') as dict_file:
        all_words = set(word for word in dict_file.read().splitlines() if valid_wordle_word(word))
    find_best_guess(all_words, words_remaining)


if __name__ == '__main__':
    main()
