from os.path import isdir
from time import time, strftime
from os import path
from base import list_dirs, Droogle, Serializer, list_files

__author__ = 'gronostaj'


def index():

    dirs = filter(lambda n: not n.startswith('.'), list_dirs('.'))
    if len(dirs) > 1:
        for i, dir in enumerate(dirs):
            print("%*d. %s" % (3, i + 1, dir))
        dirname = raw_input("Which directory should be reindexed? (number or name): ")

        if not isdir(dirname):
            dirname = dirs[int(dirname) - 1]
    else:
        dirname = dirs[0]
    inputfiles = filter(lambda f: f.endswith('.txt'), list_files(dirname))

    print("Will reindex %s" % dirname)

    start = time()
    q, w = Droogle.index(dirname, inputfiles, r'(?:\r?\n|\n)\w*(?:\r?\n|\n)')
    end = time()

    delta = end - start
    print("%d questions, %d words were indexed in %dm %ds." % (q, w, delta / 60, delta % 60))

    config = Serializer.from_json('config.json') if path.isfile('config.json') else {}
    config['index'] = dirname
    Serializer.to_json(config, 'config.json', gz=False)


if __name__ == '__main__':
    index()