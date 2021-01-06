from datetime import date
from json import loads
from os.path import join
from re import compile
from subprocess import run, PIPE


class Xmms2Ctl:
    """A controller class for xmms2 cli"""

    def __init__(self, scripts_dir: str, commands_dir: str):
        self.scripts_dir = scripts_dir
        self.commands_dir = commands_dir

    @staticmethod
    def get_status_icon(status: str):
        p = compile("^(play|pause|stop).*$")
        m = p.match(status.lower())
        return m.group(1)

    def action(self, action: str):
        run([join(self.scripts_dir, 'xmms2_action.sh'), action])

    def stop(self):
        self.action('stop')

    def start(self):
        self.action('play')

    def clear(self):
        self.action('clear')

    def toggle(self):
        self.action('toggle')

    def add_album(self, pattern: str):
        self.action('add -o partofset,tracknr album:%s' % pattern)

    def add_advent(self, pattern: str, day: int):
        self.action('add album:%s AND tracknr:%d' % (pattern, day))

    def add_url(self, url: str):
        self.action('add %s' % url)

    def add_title(self, title: str):
        self.action('add title:%s' % title)

    def play(self, kind: str, what: str):
        if kind in ['play', 'toggle', 'pause', 'stop', 'prev', 'next']:
            self.action(kind)
            return None

        if kind not in ['album', 'advent', 'url', 'title']:
            return False

        self.stop()
        self.clear()
        if kind == 'album':
            self.add_album(what)
        elif kind == 'advent':
            today = date.today()
            if today.month == 12 and today.day <= 24:
                self.add_advent(what, today.day)
            else:
                self.add_album(what)
        elif kind == 'url':
            self.add_url(what)
        elif kind == 'title':
            self.add_title(what)
        return True

    def play_card(self, card_name: str):
        with open(join(self.commands_dir, card_name), 'r') as file_:
            kind_ = file_.readline().strip()
            what_ = file_.readline().strip()
            return self.play(kind_, what_)

    def whats_playing(self):
        result = run(
            join(self.scripts_dir, 'currently_playing.sh'),
            stdout=PIPE, stderr=PIPE, universal_newlines=True
        )
        splitlines = result.stdout.splitlines()
        status = loads(splitlines[0])
        status['status_icon'] = self.get_status_icon(status['status'])
        status['play_class'] = 'pause' if status['status_icon'] == 'play' else 'play'
        return status
