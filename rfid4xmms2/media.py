from os.path import join
from subprocess import run, PIPE

from rfid4xmms2 import application

ALLOWED_FILE_EXTENSIONS = ['mp3', 'm4a']


class MediaCtl:

    def get_titles(self):
        result = run([join(application.config['SCRIPTS_DIR'], 'read_titles.sh')], stdout=PIPE, stderr=PIPE,
                     universal_newlines=True)
        if result.returncode != 0:
            application.logger.warning('read_titles.sh returned %d', result.returncode)
            return []

        titles = []
        for line in result.stdout.splitlines():
            titles.append(line)

        return titles

    def get_albums(self):
        result = run(
            [join(application.config['SCRIPTS_DIR'], 'read_albums.sh'), application.config['COMMANDS_DIR']],
            stdout=PIPE, stderr=PIPE, universal_newlines=True)
        if result.returncode != 0:
            application.logger.warning('read_albums.sh returned %d', result.returncode)
            return []

        albums = []
        for line in result.stdout.splitlines():
            albums.append(line)

        return albums

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_EXTENSIONS

    def store_files(self, tmp_dir, file):
        if file and self.allowed_file(file.filename):
            file.save(join(tmp_dir, file.filename))

    def convert_files(self, tmp_dir):
        run([join(application.config['SCRIPTS_DIR'], 'convert_m4a_to_mp3.sh'), tmp_dir])

    def move_files_to_media_lib(self, tmp_dir):
        run([
            join(application.config['SCRIPTS_DIR'], 'move_to_media_lib.sh'),
            tmp_dir,
            application.config['MEDIA_LIB']
        ])
