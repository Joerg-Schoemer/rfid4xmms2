from os import remove
from os.path import join, exists
from platform import node
from tempfile import TemporaryDirectory

from flask import render_template, request, redirect, url_for

from rfid4xmms2 import application
from rfid4xmms2.cards import CardCtl
from rfid4xmms2.media import MediaCtl
from rfid4xmms2.observer import xmms2ctl as xmms2Ctl

cardCtl = CardCtl()
mediaCtl = MediaCtl()


@application.route('/')
@application.route('/index')
def index():
    return render_template('index.html', hostname=node())


@application.route('/cards/known', methods=['GET', 'POST'])
def cards():
    if request.method == 'GET':
        return render_template('cards/known.html', cards=cardCtl.list_cards(), hostname=node())

    card_name_ = request.form['card_name']
    if request.form['action'] == 'delete':
        cardCtl.release_action(card_name_)
        return redirect(url_for('cards'))

    xmms2Ctl.play_card(card_name_)
    return redirect(url_for('player'))


@application.route('/cards/unknown', methods=['GET', 'POST'])
def unknown_cards():
    if request.method == 'GET':
        return render_template('cards/unknown.html', cards=cardCtl.list_unknown_cards(), hostname=node())

    if request.form['action'] == 'delete':
        file = join(application.config['UNKNOWN_DIR'], request.form['card_name'])
        if exists(file):
            remove(file)

    return render_template('cards/unknown.html', cards=cardCtl.list_unknown_cards(), hostname=node())


@application.route('/cards/edit', methods=['POST'])
def edit():
    if request.form['action'] == 'cancel':
        return redirect(request.form['redirect'])

    if request.form['action'] == 'save':
        cardCtl.assign_action(
            request.form['card_name'],
            request.form['card_kind'],
            request.form['card_what']
        )
        return redirect(request.form['redirect'])

    card = {
        'name': request.form['card_name'],
        'friendly_name': request.form['card_friendly_name'],
        'kind': request.form['card_kind'],
        'what': request.form['card_what'],
    }
    card_kinds = ['album', 'advent', 'next', 'prev', 'title', 'toggle', 'url']
    return render_template('cards/edit.html', card=card, card_kinds=card_kinds, redirect=request.form['redirect'],
                           hostname=node())


@application.route('/cards/assign', methods=['POST'])
def assign():
    card_name = request.form['card_name']
    if 'kind' in request.form.keys():
        kind_ = request.form['kind']
        what_ = '"' + str(request.form['what']).replace(':', '\\:') + '"'
        cardCtl.assign_action(card_name, kind_, what_)
        return redirect(url_for('unknown_cards'))

    card_friendly_name = request.form['card_friendly_name']
    return render_template('cards/assign.html', card_name=card_name, card_friendly_name=card_friendly_name,
                           albums=mediaCtl.get_albums(), hostname=node())


@application.route('/media/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'GET':
        return render_template('media/upload.html')

    files = request.files.getlist('mp3')
    with TemporaryDirectory() as tmp_dir:
        print('created temporary directory ' + tmp_dir)
        for file in files:
            if file.filename == '':
                return redirect(request.url)

            mediaCtl.store_files(tmp_dir, file)
        mediaCtl.convert_files(tmp_dir)
        mediaCtl.move_files_to_media_lib(tmp_dir)

    return redirect(url_for('unknown_cards'))


@application.route('/media/player', methods=['POST', 'GET'])
def player():
    if request.method == 'GET' or request.form['action'] == 'reload':
        return render_template('media/player.html', whats_playing=xmms2Ctl.whats_playing())

    xmms2Ctl.action(request.form['action'])
    return render_template('media/player.html', whats_playing=xmms2Ctl.whats_playing())
