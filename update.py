"""Script to update platform-specific lists from the source list."""
from re import sub, escape
from json import loads
from itertools import chain

def with_open(file: str, *, write: str = None) -> str:
    with open(file, 'w' if write else 'r') as f:
        if write:
            f.write(write)
            return write
        else:
            return f.read()

shortcuts = loads(with_open('sources/shortcuts.json'))


def go(name: str, src: str, head_footers: str, ubo_fn: str, ubl_fn: str,
       hosts_fn: str) -> None:
    print(f'### {name} ###')
    domains = []
    urls = []
    src = with_open(f'sources/{src}').splitlines()


    # Parse the file
    def add_to_list(add: str) -> None:
        if '/' in add:
            urls.append(add)
        else:
            domains.append(add)


    for i in range(len(src)):
        line = src[i].strip()

        match line[:1]:
            case '#' | '':  # comment or blank
                continue
            case '_':  # shortcut
                shortcut = sub('^|:.*$', '', line)
                content = sub('^.*:', '', line)

                if shortcut not in shortcuts:
                    raise ValueError(f'Line {i}: no shortcut {shortcut}')

                for repl in shortcuts[shortcut]:
                    add_to_list(repl.replace(' : ', content))
            case _:  # domain or URL
                add_to_list(line)

    print(f'Parsed {len(domains)} domains and {len(urls)} URL paths')


    # Generate hosts file
    hosts = with_open(f'sources/headers/{head_footers}hosts.txt') + '\n'

    for item in domains:
        hosts += f'0.0.0.0 {item}\n'
        hosts += f'0.0.0.0 www.{item}\n'

    hosts += with_open(f'sources/footers/{head_footers}hosts.txt')
    with_open(hosts_fn, write=hosts)
    print('Wrote hosts file')


    # Generate uBlock Origin (uBO) file
    ubo = with_open(f'sources/headers/{head_footers}ubo.txt') + '\n'

    for item in chain(domains, urls):
        ubo += (r'google.com,duckduckgo.com,bing.com##a:matches-prop'
                r'(href=/^(((https?:)?)\/\/)?([a-z0-9-.]*\.)?'
                f'{escape(item).replace('/', r'\/')}'
                r'(\/.*)?$/):upward(div):style(opacity:0.00!important;)'
                '\n')

    ubo += with_open(f'sources/footers/{head_footers}ubo.txt')
    with_open(ubo_fn, write=ubo)
    print('Wrote uBlock Origin file')


    # Generate uBlacklist file
    ubl = with_open(f'sources/headers/{head_footers}ublacklist.txt') + '\n'
    for item in chain(domains, urls):
        ubl += (r'/^(((https?:)?)\/\/)?([a-z0-9-.]*\.)?'
                f'{escape(item).replace('/', r'\/')}'
                r'(\/.*)?$/'
                '\n')

    ubl += with_open(f'sources/footers/{head_footers}ublacklist.txt')
    with_open(ubl_fn, write=ubl)
    print('Wrote uBlacklist file')


if __name__ == '__main__':
    for t in [
        {'name': 'Regular', 'src': 'list.txt', 'head_footers': '',
         'ubo_fn': 'list.txt', 'ubl_fn': 'list_uBlacklist.txt',
         'hosts_fn': 'noai_hosts.txt'},

        {'name': 'Nuclear', 'src': 'nuclear.txt', 'head_footers': 'nuclear/',
         'ubo_fn': 'additional_list_nuclear.txt',
         'ubl_fn': 'list_uBlacklist_nuclear.txt',
         'hosts_fn': 'noai_hosts_nuclear.txt'}
    ]:
        go(**t)
