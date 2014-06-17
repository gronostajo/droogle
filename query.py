from __future__ import print_function

from os import path
from base import Serializer, Droogle, FileMissingError

__author__ = 'gronostaj'


def query():

    config = {
        'index': '',
        'results': 5
    }
    if path.isfile('config.json'):
        config.update(Serializer.from_json('config.json'))

    if not len(config['index']):
        print("No index directory is configured. Create a directory, put Drill files inside and index it.")
        exit(1)
    elif not path.isdir(config['index']):
        print("Directory %s doesn't exist. Create it, copy Drill files into it and index it." % config['index'])
        exit(1)

    try:
        droogle = Droogle(config['index'])
    except FileMissingError, (ex):
        print(
            "Some index file is missing in %s: %s.\nAllowed extensions are:" % (config['index'], ex.filename),
            ', '.join(map(lambda s: s[2:], Droogle.SUFFIXES))
        )
        exit(1)

    while True:
        string = raw_input("Enter your query: ")
        if not string:
            break
        results = droogle.query(string)
        for i, result in enumerate(results[:config['results']]):
            print("\n=== Result %d ===\n%s\n" % (i + 1, result))


if __name__ == '__main__':
    query()