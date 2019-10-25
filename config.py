import configparser
import zlib
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d


def obscure(data):
    return b64e(zlib.compress(str.encode(data), 9)).decode('utf-8')


def unobscure(obscured):
    return zlib.decompress(b64d(str.encode(obscured))).decode('utf-8')


def registry(filename, tag, key, secret):
    with open(filename, 'w') as file:
        file.write(f'[{tag}]\n')
        file.write(f'KEY = {obscure(key)}\n')
        file.write(f'SECRET = {obscure(secret)}\n\n')


def rescue(filename, tag):
    config = configparser.ConfigParser()
    config.read(filename)
    return unobscure(config[tag]['KEY']), unobscure(config[tag]['SECRET'])


def main():
    pass


if __name__ == '__main__':
    main()


