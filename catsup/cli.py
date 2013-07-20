import sys
import os

major = sys.version_info[0]
if major < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from catsup.options import g
from catsup.logger import logger, enable_pretty_logging

enable_pretty_logging()

g.catsup_path = os.path.abspath(os.path.dirname(__file__))
g.public_templates_path = os.path.join(g.catsup_path, 'templates')
g.cwdpath = os.path.abspath('.')

try:
    import catsup
except ImportError:
    import site
    site.addsitedir(os.path.dirname(g.catsup_path))

doc = """catsup v%s

Usage:
    catsup init [<path>]
    catsup build [-s <file>|--settings=<file>]
    catsup deploy [-s <file>|--settings=<file>]
    catsup git [-s <file>|--settings=<file>]
    catsup rsync [-s <file>|--settings=<file>]
    catsup server [-s <file>|--settings=<file>] [-p <port>|--port=<port>]
    catsup webhook [-s <file>|--settings=<file>] [-p <port>|--port=<port>]
    catsup themes
    catsup install <theme>
    catsup migrate --wordpress -f <file>|--file=<file> [-o <dir>|--output=<dir>]
    catsup -h | --help
    catsup --version

Options:
    -h --help               Show this screen and exit.
    -s --settings=<file>    specify a config file. [default: config.json]
    -f --file=<file>        specify a wordpress output file.
    -o --output=<dir>       specify a output folder. [default: .]
    -p --port=<port>        specify the server port. [default: 8888]
    -g --global             install theme to global theme folder.
""" % catsup.__version__

from parguments import Parguments

parguments = Parguments(doc, version=catsup.__version__)


@parguments.command
def init(path):
    """
    Usage:
        catsup init [<path>]

    Options:
        -h --help               Show this screen and exit.
    """
    from catsup.parser.utils import create_config_file
    create_config_file(path)


@parguments.command
def build(settings):
    """
    Usage:
        catsup build [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    from catsup.generator import Generator
    generator = Generator(settings)
    generator.generate()


@parguments.command
def deploy(settings):
    """
    Usage:
        catsup deploy [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    import catsup.parser
    import catsup.deploy
    config = catsup.parser.config(settings)
    if config.deploy.default == 'git':
        catsup.deploy.git()
    elif config.deploy.default == 'rsync':
        catsup.deploy.rsync()
    else:
        logger.error("Unknown deploy: %s" % config.deploy.default)


@parguments.command
def git(settings):
    """
    Usage:
        catsup git [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    import catsup.parser.config
    import catsup.deploy
    catsup.parser.config.load(settings)
    catsup.deploy.git()


@parguments.command
def rsync(settings):
    """
    Usage:
        catsup rsync [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    import catsup.parser.config
    import catsup.deploy
    catsup.parser.config.load(settings)
    catsup.deploy.rsync()


@parguments.command
def server(settings, port):
    """
    Usage:
        catsup server [-s <file>|--settings=<file>] [-p <port>|--port=<port>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
        -p --port=<port>        specify the server port. [default: 8888]
    """
    import catsup.server
    server = catsup.server.PreviewServer(settings, port)
    server.run()


@parguments.command
def webhook(settings, port):
    """
    Usage:
        catsup webhook [-s <file>|--settings=<file>] [-p <port>|--port=<port>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
        -p --port=<port>        specify the server port. [default: 8888]
    """
    import catsup.parser.config
    import catsup.server
    catsup.parser.config.load(settings)
    catsup.server.webhook(port=port)


@parguments.command
def themes():
    """
    Usage:
        catsup themes

    Options:
        -h --help               Show this screen and exit.
    """
    import catsup.themes
    catsup.themes.list()


@parguments.command
def install(theme):
    """
    Usage:
        catsup install <theme>

    Options:
        -h --help               Show this screen and exit.
    """
    import catsup.themes
    catsup.themes.install(path=theme)


@parguments.command
def migrate(wordpress, file, output):
    """
    Usage:
        catsup migrate --wordpress -f <file>|--file=<file> [-o <dir>|--output=<dir>]

    Options:
        -h --help               Show this screen and exit.
        -f --file=<file>        specify a wordpress output file.
        -o --output=<dir>       specify a output folder. [default: .]
    """
    import catsup.migrate
    if wordpress:
        catsup.migrate.wordpress(file, output)


def main():
    parguments.run()


if __name__ == '__main__':
    if "--hotshot" in sys.argv:
        sys.argv.remove("--hotshot")
        import hotshot
        prof = hotshot.Profile("catsup.prof")
        prof.runcall(parguments.run)
        prof.stop()
    else:
        parguments.run()
