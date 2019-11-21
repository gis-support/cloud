import pytest
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''Przeprowadza testy. Przy braku argumentów przeprowadza wszystkie testy.'''
    )
    parser_group = parser.add_argument_group(
        'Test driven development', 'Uruchamianie wybranych grup testów')
    parser_group_ex = parser_group.add_mutually_exclusive_group()
    parser_group_ex.add_argument(
        '-g', '--groups', dest="groups", nargs='*', help='Wybrane grupy: auth, layers, features')
    args = parser.parse_args()
    if args.groups:
        pytest.main(['-s', '-x', '-m', ' or '.join(args.groups)])
    else:
        pytest.main(['-s', '-x'])
