from datetime import datetime
from os import rename, scandir
from os.path import join

from rfid4xmms2 import application


class CardCtl:
    """A class to manage cards"""

    def list_unknown_cards(self):
        cards = []
        unknown_dir = application.config['UNKNOWN_DIR']
        with scandir(unknown_dir) as entries:
            for entry in entries:
                cards.append({
                    'name': entry.name,
                    'friendly_name': str(entry.name).replace('.cmd', '').replace('_', ':'),
                    'mtime': datetime.fromtimestamp(entry.stat().st_mtime),
                })
        cards.sort(key=lambda item: item['mtime'], reverse=True)
        return cards

    def list_cards(self):
        cards = []
        commands_dir = application.config['COMMANDS_DIR']
        with scandir(commands_dir) as entries:
            for entry in entries:
                with open(join(commands_dir, entry.name), 'r') as file_:
                    kind_ = file_.readline().strip()
                    what_ = file_.readline().replace('"', '')
                    if kind_ in ['play', 'next', 'prev', 'toggle']:
                        continue
                    cards.append({
                        'name': entry.name,
                        'friendly_name': str(entry.name).replace('.cmd', '').replace('_', ':'),
                        'mtime': datetime.fromtimestamp(entry.stat().st_mtime),
                        'kind': kind_,
                        'what': str(what_).replace('\\:', ':'),
                    })
        cards.sort(key=lambda item: item['what'])
        cards.sort(key=lambda item: item['kind'])
        return cards

    def assign_action(self, card_name_: str, kind_: str, what_: str):
        unknown_dir_ = application.config['UNKNOWN_DIR']
        commands_dir_ = application.config['COMMANDS_DIR']
        with open(join(unknown_dir_, card_name_), 'w') as file_:
            if kind_ == 'url':
                file_.write("\n".join([kind_, what_]) + '\n')
            else:
                file_.write("\n".join([kind_, '"' + what_.replace(':', '\\:') + '"']) + '\n')
        rename(join(unknown_dir_, card_name_), join(commands_dir_, card_name_))

    def release_action(self, card_name_: str):
        unknown_dir_ = application.config['UNKNOWN_DIR']
        commands_dir_ = application.config['COMMANDS_DIR']
        rename(join(commands_dir_, card_name_), join(unknown_dir_, card_name_))
