#  _  __
# | |/ /___ ___ _ __  ___ _ _ ®
# | ' </ -_) -_) '_ \/ -_) '_|
# |_|\_\___\___| .__/\___|_|
#              |_|
#
# Keeper Commander
# Copyright 2021 Keeper Security Inc.
# Contact: ops@keepersecurity.com
#


import argparse
import logging
import requests
import json
import os
import getpass

from typing import Optional, List
from contextlib import contextmanager
from .. import api
from . import imp_exp
from ..params import KeeperParams
from ..commands.base import raise_parse_exception, suppress_exit, user_choice, Command
from .importer import Attachment as ImportAttachment, SharedFolder, Permission
from .lastpass import fetcher
from .lastpass.vault import Vault
from .json.json import KeeperJsonImporter, KeeperJsonExporter


def register_commands(commands):
    commands['import'] = RecordImportCommand()
    commands['export'] = RecordExportCommand()
    commands['unload-membership'] = UnloadMembershipCommand()
    commands['load-membership'] = LoadMembershipCommand()


def register_command_info(aliases, command_info):
    for p in [import_parser, export_parser]:
        command_info[p.prog] = p.description


import_parser = argparse.ArgumentParser(prog='import', description='Import data from a local file into Keeper.')
import_parser.add_argument('--display-csv', '-dc', dest='display_csv', action='store_true',  help='display Keeper CSV import instructions')
import_parser.add_argument('--display-json', '-dj', dest='display_json', action='store_true',  help='display Keeper JSON import instructions')
import_parser.add_argument('--old-domain', '-od', dest='old_domain', action='store',  help='old domain for changing user emails in permissions')
import_parser.add_argument('--new-domain', '-nd', dest='new_domain', action='store',  help='new domain for changing user emails in permissions')
import_parser.add_argument('--format', dest='format', choices=['json', 'csv', 'keepass', 'lastpass'], required=True, help='file format')
import_parser.add_argument('--folder', dest='folder', action='store', help='import into a separate folder.')
import_parser.add_argument('-s', '--shared', dest='shared', action='store_true', help='import folders as Keeper shared folders')
import_parser.add_argument('-p', '--permissions', dest='permissions', action='store', help='default shared folder permissions: manage (U)sers, manage (R)ecords, can (E)dit, can (S)hare, or (A)ll, (N)one')
import_parser.add_argument('--update',  dest='update',  action='store_true',  help='Update records with common login, url or title')
import_parser.add_argument('--users',  dest='users',  action='store_true',  help='Update shared folder user permissions only')
import_parser.add_argument('name', type=str, help='file name (json, csv, keepass) or account name (lastpass)')
import_parser.error = raise_parse_exception
import_parser.exit = suppress_exit


export_parser = argparse.ArgumentParser(prog='export', description='Export data from Keeper to a local file.')
export_parser.add_argument('--format', dest='format', choices=['json', 'csv', 'keepass'], required=True, help='file format')
export_parser.add_argument('--max-size', dest='max_size', help='Maximum file attachment file. Example: 100K, 50M, 2G. Default: 10M')
export_parser.add_argument('-kp', '--keepass-file-password', dest='keepass_file_password', action='store', help='Password for the exported Keepass file')
export_parser.add_argument('name', type=str, nargs='?', help='file name or console output if omitted (except keepass)')
export_parser.error = raise_parse_exception
export_parser.exit = suppress_exit


unload_membership_parser = argparse.ArgumentParser(prog='unload-membership', description='Unload shared folder membership to JSON file.')
unload_membership_parser.add_argument('--source', dest='source', choices=['keeper', 'lastpass'], required=True, help='Shared folder membership source')
unload_membership_parser.add_argument('name', type=str, nargs='?', help='Output file name. "shared_folder_membership.json" if omitted.')
unload_membership_parser.error = raise_parse_exception
unload_membership_parser.exit = suppress_exit


load_membership_parser = argparse.ArgumentParser(prog='unload-membership', description='Unload shared folder membership to JSON file.')
load_membership_parser.add_argument('name', type=str, nargs='?', help='Output file name. "shared_folder_membership.json" if omitted.')
load_membership_parser.error = raise_parse_exception
load_membership_parser.exit = suppress_exit

csv_instructions = '''CSV Import Instructions

File Format:
Folder,Title,Login,Password,Website Address,Notes,Custom Fields

• To specify subfolders, use backslash "\\" between folder names
• To make a shared folder specify the name or path to it in the 7th field

Example 1: Create a regular folder at the root level with 2 custom fields
My Business Stuff,Twitter,marketing@company.com,123456,https://twitter.com,These are some notes,,API Key,5555,Date Created, 2018-04-02

Example 2: Create a shared subfolder inside another folder with edit and re-share permission
Personal,Twitter,craig@gmail.com,123456,https://twitter.com,,Social Media#edit#reshare

To load the sample data:
import --format=csv sample_data/import.csv
'''

json_instructions = '''JSON Import Instructions

Example JSON import file can be found in sample_data/import.json.txt.

The JSON file supports creating records, folders and shared folders.

Within shared folders, you can also automatically assign user or team permissions.

To load the sample file into your vault, run this command:
import --format=json sample_data/import.json.txt
'''


class KeeperAttachment(ImportAttachment):
    # FIXME: Note that this may be a duplicate of keepercommander/importer/imp_exp.py's KeeperAttachment.
    def __init__(self, params, record_uid,):
        ImportAttachment.__init__(self)
        self.params = params
        self.record_uid = record_uid

    @contextmanager
    def open(self):
        rq = {
            'command': 'request_download',
            'file_ids': [self.file_id],
        }
        api.resolve_record_access_path(self.params, self.record_uid, path=rq)

        rs = api.communicate(self.params, rq)
        if rs['result'] == 'success':
            dl = rs['downloads'][0]
            if 'url' in dl:
                with requests.get(dl['url'], stream=True) as rq_http:
                    yield rq_http.raw


class ImporterCommand(Command):
    def execute_args(self, params, args, **kwargs):
        if args.find('--display-csv') >= 0 or args.find('-dc') >= 0:
            print(csv_instructions)
        elif args.find('--display-json') >= 0 or args.find('-dj') >= 0:
            print(json_instructions)
        else:
            Command.execute_args(self, params, args, **kwargs)


class RecordImportCommand(ImporterCommand):
    def get_parser(self):
        return import_parser

    def execute(self, params, **kwargs):
        update_flag = kwargs['update'] if 'update' in kwargs else False
        import_format = kwargs['format'] if 'format' in kwargs else None
        import_name = kwargs['name'] if 'name' in kwargs else None
        shared = kwargs.get('shared') or False
        manage_users = False
        manage_records = False
        can_edit = False
        can_share = False
        if import_format and import_name:
            permissions = kwargs.get('permissions')
            if shared and not permissions:
                permissions = user_choice('Default shared folder permissions: manage (U)sers, manage (R)ecords, can (E)dit, can (S)hare, or (A)ll, (N)one', 'uresan', show_choice=False, multi_choice=True)
            if permissions:
                chars = set()
                chars.update([x for x in permissions.lower()])
                if 'a' in chars:
                    manage_users = True
                    manage_records = True
                    can_edit = True
                    can_share = True
                else:
                    if 'u' in chars:
                        manage_users = True
                    if 'r' in chars:
                        manage_records = True
                    if 'e' in chars:
                        can_edit = True
                    if 's' in chars:
                        can_share = True

            logging.info('Processing... please wait.')
            imp_exp._import(params, import_format, import_name, shared=shared, import_into=kwargs.get('folder'),
                            manage_users=manage_users, manage_records=manage_records, users_only=kwargs.get('users') or False,
                            can_edit=can_edit, can_share=can_share, update_flag=update_flag,
                            old_domain=kwargs.get('old_domain'), new_domain=kwargs.get('new_domain'))
        else:
            logging.error('Missing argument')


class RecordExportCommand(ImporterCommand):
    def get_parser(self):
        return export_parser

    def execute(self, params, **kwargs):

        if is_export_restricted(params):
            logging.warning('Permissions Required: `export` command is disabled. Please contact your enterprise administrator.')
            return

        export_format = kwargs['format'] if 'format' in kwargs else None
        export_name = kwargs['name'] if 'name' in kwargs else None

        extra = {}
        if kwargs.get('keepass_file_password'):
            extra['keepass_file_password'] = kwargs.get('keepass_file_password')

        if format:
            logging.info('Processing... please wait.')
            msize = kwargs.get('max_size')    # type: str
            if msize:
                multiplier = 1
                scale = msize[-1].upper()
                if scale == 'K':
                    multiplier = 1024
                elif scale == 'M':
                    multiplier = 1024 ** 2
                elif scale == 'G':
                    multiplier = 1024 ** 3

                if multiplier != 1:
                    msize = msize[:-1]
                try:
                    max_size = int(msize) * multiplier
                    extra['max_size'] = max_size
                except ValueError:
                    logging.error('Invalid maximum attachment file size parameter: %s', kwargs.get('max_size'))
                    return

            imp_exp.export(params, export_format, export_name, **extra)
        else:
            logging.error('Missing argument')


def is_export_restricted(params):
    is_export_restricted = False

    booleans = params.enforcements['booleans'] if params.enforcements and 'booleans' in params.enforcements else []

    if len(booleans) > 0:
        restrict_export_boolean = next((s for s in booleans if s['key'] == 'restrict_export'), None)

        if restrict_export_boolean:
            is_export_restricted = restrict_export_boolean['value']

    return is_export_restricted


class UnloadMembershipCommand(Command):
    def get_parser(self):  # type: () -> Optional[argparse.ArgumentParser]
        return unload_membership_parser

    def execute(self, params, **kwargs):  # type: (KeeperParams, **any) -> any
        source = kwargs.get('source') or 'keeper'
        file_name = kwargs.get('name') or 'shared_folder_membership.json'

        shared_folders = []  # type: List[SharedFolder]

        json_importer = KeeperJsonImporter()

        if os.path.exists(file_name):
            for sf in json_importer.do_import(file_name, users_only=True):
                if isinstance(sf, SharedFolder):
                    shared_folders.append(sf)

        json_shared_folders = set((x.uid for x in shared_folders))

        added_members = []  # type: List[SharedFolder]
        if source == 'keeper':
            if params.shared_folder_cache:
                for shared_folder_uid in params.shared_folder_cache:
                    if shared_folder_uid in json_shared_folders:
                        continue
                    shared_folder = api.get_shared_folder(params, shared_folder_uid)
                    sf = SharedFolder()
                    sf.uid = shared_folder.shared_folder_uid
                    sf.path = imp_exp.get_folder_path(params, shared_folder.shared_folder_uid)
                    sf.manage_users = shared_folder.default_manage_users
                    sf.manage_records = shared_folder.default_manage_records
                    sf.can_edit = shared_folder.default_can_edit
                    sf.can_share = shared_folder.default_can_share
                    sf.permissions = []
                    if shared_folder.teams:
                        for team in shared_folder.teams:
                            perm = Permission()
                            perm.uid = team['team_uid']
                            perm.name = team['name']
                            perm.manage_users = team['manage_users']
                            perm.manage_records = team['manage_records']
                            sf.permissions.append(perm)
                    if shared_folder.users:
                        for user in shared_folder.users:
                            perm = Permission()
                            perm.name = user['username']
                            perm.manage_users = user['manage_users']
                            perm.manage_records = user['manage_records']
                            sf.permissions.append(perm)
                    added_members.append(sf)

        elif source == 'lastpass':
            username = input('...' + 'LastPass Username'.rjust(30) + ': ')
            if not username:
                logging.warning('LastPass username is required')
                return
            password = getpass.getpass(prompt='...' + 'LastPass Password'.rjust(30) + ': ', stream=None)
            if not password:
                logging.warning('LastPass password is required')
                return

            print('Press <Enter> if account is not protected with Multifactor Authentication')
            twofa_code = getpass.getpass(prompt='...' + 'Multifactor Password'.rjust(30) + ': ', stream=None)
            if not twofa_code:
                twofa_code = None

            session = None
            try:
                session = fetcher.login(username, password, twofa_code, None)
                blob = fetcher.fetch(session)
                encryption_key = blob.encryption_key(username, password)
                vault = Vault(blob, encryption_key, session, False)

                lastpass_shared_folder = [x for x in vault.shared_folders]

                for lpsf in lastpass_shared_folder:
                    if lpsf.id in json_shared_folders:
                        continue

                    logging.info('Loading shared folder membership for "%s"', lpsf.name)

                    members, teams, error = fetcher.fetch_shared_folder_members(session, lpsf.id)
                    sf = SharedFolder()
                    sf.uid = lpsf.id
                    sf.path = lpsf.name
                    sf.permissions = []
                    if members:
                        sf.permissions.extend((self._lastpass_permission(x) for x in members))
                    if teams:
                        sf.permissions.extend((self._lastpass_permission(x) for x in teams))
                    added_members.append(sf)
            except Exception as e:
                logging.warning(e)
            finally:
                if session:
                    fetcher.logout(session)

        if added_members:
            shared_folders.extend(added_members)
            json_exporter = KeeperJsonExporter()
            json_exporter.do_export(file_name, shared_folders)
            logging.info('%d shared folder memberships unloaded.', len(added_members))
        else:
            logging.info('No folders unloaded')

    @staticmethod
    def _lastpass_permission(lp_permission):  # type: (dict) -> Permission
        permission = Permission()
        permission.name = lp_permission['username']
        permission.manage_records = lp_permission['readonly'] == '0'
        permission.manage_users = lp_permission['can_administer'] == '1'
        return permission


class LoadMembershipCommand(Command):
    def get_parser(self):  # type: () -> Optional[argparse.ArgumentParser]
        return load_membership_parser

    def execute(self, params, **kwargs):  # type: (KeeperParams, **any) -> any
        file_name = kwargs.get('name') or 'shared_folder_membership.json'
        if not os.path.exists(file_name):
            logging.warning('Shared folder membership file "%s" no found', file_name)
            return

        file_name = kwargs.get('name') or 'shared_folder_membership.json'

        shared_folders = []  # type: List[SharedFolder]

        if os.path.exists(file_name):
            json_importer = KeeperJsonImporter()
            for sf in json_importer.do_import(file_name, users_only=True):
                if isinstance(sf, SharedFolder):
                    shared_folders.append(sf)

        if len(shared_folders) > 0:
            imp_exp.import_user_permissions(params, shared_folders)
