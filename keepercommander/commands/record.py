#  _  __
# | |/ /___ ___ _ __  ___ _ _ ®
# | ' </ -_) -_) '_ \/ -_) '_|
# |_|\_\___\___| .__/\___|_|
#              |_|
#
# Keeper Commander
# Copyright 2022 Keeper Security Inc.
# Contact: ops@keepersecurity.com
#

import argparse
import datetime
import logging
import fnmatch
import re
from typing import Dict, Any

from .base import dump_report_data, user_choice, Command, GroupCommand
from .. import api, display, crypto, utils, vault, vault_extensions
from ..team import Team

from ..params import KeeperParams
from ..subfolder import try_resolve_path


def register_commands(commands):
    commands['search'] = SearchCommand()
    commands['trash'] = TrashCommand()
    commands['list'] = RecordListCommand()
    commands['list-sf'] = RecordListSfCommand()
    commands['list-team'] = RecordListTeamCommand()


def register_command_info(aliases, command_info):
    aliases['s'] = 'search'
    aliases['l'] = 'list'
    aliases['lsf'] = 'list-sf'
    aliases['lt'] = 'list-team'

    for p in [search_parser, list_parser, list_sf_parser, list_team_parser]:
        command_info[p.prog] = p.description
    command_info['trash'] = 'Manage deleted items'


search_parser = argparse.ArgumentParser(prog='search', description='Search the vault. Can use a regular expression.')
search_parser.add_argument('pattern', nargs='?', type=str, action='store', help='search pattern')
search_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose output')
search_parser.add_argument('-c', '--categories', dest='categories', action='store',
                           help='One or more of these letters for categories to search: "r" = records, '
                                '"s" = shared folders, "t" = teams')


list_parser = argparse.ArgumentParser(prog='list', description='List records.')
list_parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose output')
list_parser.add_argument('--format', dest='format', action='store', choices=['csv', 'json', 'table'], default='table',
                         help='output format')
list_parser.add_argument('--output', dest='output', action='store',
                         help='output file name. (ignored for table format)')
list_parser.add_argument('-t', '--type', dest='record_type', action='append',
                         help='List records of certain types. Can be repeated')
list_parser.add_argument('pattern', nargs='?', type=str, action='store', help='search pattern')


list_sf_parser = argparse.ArgumentParser(prog='list-sf', description='List shared folders.')
list_sf_parser.add_argument('--format', dest='format', action='store', choices=['csv', 'json', 'table'],
                            default='table', help='output format')
list_sf_parser.add_argument('--output', dest='output', action='store',
                            help='output file name. (ignored for table format)')
list_sf_parser.add_argument('pattern', nargs='?', type=str, action='store', help='search pattern')


list_team_parser = argparse.ArgumentParser(prog='list-team', description='List teams.')
list_team_parser.add_argument('--format', dest='format', action='store', choices=['csv', 'json', 'table'],
                              default='table', help='output format')
list_team_parser.add_argument('--output', dest='output', action='store',
                              help='output file name. (ignored for table format)')


def find_record(params, record_name):  # type: (KeeperParams, str) -> vault.KeeperRecord
    record_uid = None
    if record_name in params.record_cache:
        record_uid = record_name
    else:
        rs = try_resolve_path(params, record_name)
        if rs is not None:
            folder, record_name = rs
            if folder is not None and record_name is not None:
                folder_uid = folder.uid or ''
                if folder_uid in params.subfolder_record_cache:
                    for uid in params.subfolder_record_cache[folder_uid]:
                        r = api.get_record(params, uid)
                        if r.title.lower() == record_name.lower():
                            record_uid = uid
                            break
    if not record_uid:
        raise Exception(f'Record "{record_name}" not found.')

    return vault.KeeperRecord.load(params, record_uid)


class SearchCommand(Command):
    def get_parser(self):
        return search_parser

    def execute(self, params, **kwargs):
        pattern = (kwargs['pattern'] if 'pattern' in kwargs else None) or ''
        if pattern == '*':
            pattern = '.*'

        categories = (kwargs.get('categories') or 'rst').lower()
        verbose = kwargs.get('verbose', False)
        skip_details = not verbose

        # Search records
        if 'r' in categories:
            results = api.search_records(params, pattern)
            if results:
                print('')
                display.formatted_records(results, verbose=verbose)

        # Search shared folders
        if 's' in categories:
            results = api.search_shared_folders(params, pattern)
            if results:
                print('')
                display.formatted_shared_folders(results, params=params, skip_details=skip_details)

        # Search teams
        if 't' in categories:
            results = api.search_teams(params, pattern)
            if results:
                print('')
                display.formatted_teams(results, params=params, skip_details=skip_details)


class RecordListCommand(Command):
    def get_parser(self):
        return list_parser

    def execute(self, params, **kwargs):
        verbose = kwargs.get('verbose', False)
        fmt = kwargs.get('format', 'table')
        pattern = kwargs['pattern'] if 'pattern' in kwargs else None
        record_type = kwargs['record_type'] if 'record_type' in kwargs else None

        records = [x for x in vault_extensions.find_records(params, pattern, record_type)
                   if (True if (verbose or record_type) else x.version in {2, 3})]
        if any(records):
            table = []
            headers = ['record_uid', 'type', 'title', 'description'] if fmt == 'json' else \
                ['Record UID', 'Type', 'Title', 'Description']
            for record in records:
                row = [record.record_uid, record.record_type, record.title,
                       vault_extensions.get_record_description(record)]
                table.append(row)
            table.sort(key=lambda x: (x[2] or '').lower())

            return dump_report_data(table, headers, fmt=fmt, filename=kwargs.get('output'),
                                    row_number=True, column_width=None if verbose else 40)
        else:
            logging.info('No records are found')


class RecordListSfCommand(Command):
    def get_parser(self):
        return list_sf_parser

    def execute(self, params, **kwargs):
        fmt = kwargs.get('format', 'table')
        pattern = kwargs['pattern'] if 'pattern' in kwargs else None
        results = api.search_shared_folders(params, pattern or '')
        if any(results):
            table = []
            headers = ['shared_folder_uid', 'name'] if fmt == 'json' else ['Shared Folder UID', 'Name']
            for sf in results:
                row = [sf.shared_folder_uid, sf.name]
                table.append(row)
            table.sort(key=lambda x: (x[1] or '').lower())

            return dump_report_data(table, headers, fmt=fmt, filename=kwargs.get('output'),
                                    row_number=True)
        else:
            logging.info('No shared folders are found')


class RecordListTeamCommand(Command):
    def get_parser(self):
        return list_team_parser

    def execute(self, params, **kwargs):
        fmt = kwargs.get('format', 'table')
        api.load_available_teams(params)
        results = []
        if type(params.available_team_cache) == list:
            for team in params.available_team_cache:
                team = Team(team_uid=team['team_uid'], name=team['team_name'])
                results.append(team)
        if any(results):
            table = []
            headers = ['team_uid', 'name'] if fmt == 'json' else ['Team UID', 'Name']
            for team in results:
                row = [team.team_uid, team.name]
                table.append(row)
            table.sort(key=lambda x: (x[1] or '').lower())

            return dump_report_data(table, headers, fmt=fmt, filename=kwargs.get('output'),
                                    row_number=True)
        else:
            logging.info('No teams are found')


trash_list_parser = argparse.ArgumentParser(prog='trash list', description='Displays a list of deleted records.')
trash_list_parser.add_argument('--format', dest='format', action='store', choices=['csv', 'json', 'table'],
                               default='table', help='output format')
trash_list_parser.add_argument('--output', dest='output', action='store',
                               help='output file name. (ignored for table format)')
trash_list_parser.add_argument('--reload', dest='reload', action='store_true', help='reload deleted records')
trash_list_parser.add_argument('pattern', nargs='?', type=str, action='store', help='search pattern')


trash_get_parser = argparse.ArgumentParser(prog='trash get', description='Get the details of a deleted record.')
trash_get_parser.add_argument('record', action='store', help='Deleted record UID')

trash_restore_parser = argparse.ArgumentParser(prog='trash restore', description='Restores deleted records.')
trash_restore_parser.add_argument('-f', '--force', dest='force', action='store_true',
                                  help='do not prompt for confirmation')
trash_restore_parser.add_argument('records', nargs='+', type=str, action='store',
                                  help='Record UID or search pattern')


class TrashMixin:
    last_revision = 0
    deleted_record_cache = {}

    @staticmethod
    def get_deleted_records(params, reload=False):    # type: (KeeperParams, bool) -> Dict[str, Any]
        if params.revision != TrashMixin.last_revision or reload:
            deleted_uids = set()
            rq = {
                'command': 'get_deleted_records',
                'client_time': utils.current_milli_time()
            }
            rs = api.communicate(params, rq)
            if 'records' in rs:
                for record in rs['records']:
                    record_uid = record['record_uid']
                    deleted_uids.add(record_uid)
                    if record_uid in TrashMixin.deleted_record_cache:
                        continue
                    try:
                        key_type = record['record_key_type']
                        record_key = utils.base64_url_decode(record['record_key'])
                        if key_type == 1:
                            record_key = crypto.decrypt_aes_v1(record_key, params.data_key)
                        elif key_type == 2:
                            record_key = api.decrypt_rsa(record_key, params.rsa_key)
                        elif key_type == 3:
                            record_key = crypto.decrypt_aes_v2(record_key, params.data_key)
                        elif key_type == 4:
                            record_key = crypto.decrypt_ec(record_key, params.ecc_key)
                        else:
                            logging.debug('Cannot decrypt record key %s', record_uid)
                            continue
                        record['record_key_unencrypted'] = record_key

                        data = utils.base64_url_decode(record['data'])
                        version = record['version']
                        record['data_unencrypted'] = \
                            crypto.decrypt_aes_v2(data, record_key) if version >= 3 else \
                                crypto.decrypt_aes_v1(data, record_key)

                        TrashMixin.deleted_record_cache[record_uid] = record
                    except Exception as e:
                        logging.debug('Cannot decrypt deleted record %s: %s', record_uid, e)

            for record_uid in list(TrashMixin.deleted_record_cache.keys()):
                if record_uid not in deleted_uids:
                    del TrashMixin.deleted_record_cache[record_uid]

        TrashMixin.last_revision = params.revision
        return TrashMixin.deleted_record_cache


class TrashCommand(GroupCommand):
    def __init__(self):
        super(TrashCommand, self).__init__()
        self.register_command('list', TrashListCommand())
        self.register_command('get', TrashGetCommand())
        self.register_command('restore', TrashRestoreCommand())
        self.default_verb = 'list'


class TrashListCommand(Command, TrashMixin):
    def get_parser(self):
        return trash_list_parser

    def execute(self, params, **kwargs):
        deleted_records = self.get_deleted_records(params, kwargs.get('reload', False))
        if len(deleted_records) == 0:
            logging.info('Trash is empty')
            return

        pattern = kwargs.get('pattern')
        if pattern:
            if pattern == '*':
                pattern = None

        title_pattern = None
        if pattern:
            title_pattern = re.compile(fnmatch.translate(pattern), re.IGNORECASE)

        table = []
        headers = ['Record UID', 'Title', 'Type', 'Deleted']

        for rec in deleted_records.values():
            record = vault.KeeperRecord.load(params, rec)

            if pattern:
                if pattern == record.record_uid:
                    pass
                elif title_pattern and title_pattern.match(record.title):
                    pass
                else:
                    continue

            deleted = rec.get('date_deleted', 0)
            if deleted:
                deleted = datetime.datetime.fromtimestamp(int(deleted / 1000))
            else:
                deleted = None
            table.append([record.record_uid, record.title, record.record_type, deleted])

        table.sort(key=lambda x: x[1].casefold())

        return dump_report_data(table, headers, fmt=kwargs.get('format'),
                                filename=kwargs.get('output'), row_number=True)


class TrashGetCommand(Command, TrashMixin):
    def get_parser(self):
        return trash_get_parser

    def execute(self, params, **kwargs):
        deleted_records = self.get_deleted_records(params)
        if len(deleted_records) == 0:
            logging.info('Trash is empty')
            return

        record_uid = kwargs.get('record')
        if not record_uid:
            logging.info('Record UID parameter is required')
            return

        rec = deleted_records.get(record_uid)
        if not rec:
            logging.info('%s is not a valid deleted record UID', record_uid)
            return

        record = vault.KeeperRecord.load(params, rec)
        if not record:
            logging.info('Cannot restore record %s', record_uid)
            return

        for name, value in record.enumerate_fields():
            if value:
                if isinstance(value, list):
                    value = '\n'.join(value)
                if len(value) > 100:
                    value = value[:99] + '...'
                print('{0:>20s}: {1}'.format(name, value))


class TrashRestoreCommand(Command, TrashMixin):
    def get_parser(self):
        return trash_restore_parser

    def execute(self, params, **kwargs):
        deleted_records = self.get_deleted_records(params)
        if len(deleted_records) == 0:
            logging.info('Trash is empty')
            return

        records = kwargs.get('records')
        if not isinstance(records, (tuple, list)):
            records = None
        if not records:
            logging.info('records parameter is empty.')
            return

        to_restore = set()
        for rec in records:
            if rec in deleted_records:
                to_restore.add(rec)
            else:
                title_pattern = re.compile(fnmatch.translate(rec), re.IGNORECASE)
                for record_uid, del_rec in deleted_records.items():
                    if record_uid in to_restore:
                        continue
                    record = vault.KeeperRecord.load(params, del_rec)
                    if title_pattern.match(record.title):
                        to_restore.add(record_uid)

        if len(to_restore) == 0:
            logging.info('There are no records to restore')
            return

        if not kwargs.get('force'):
            answer = user_choice(f'Do you want to restore {len(to_restore)} record(s)?', 'yn', default='n')
            if answer.lower() == 'y':
                answer = 'yes'
            if answer.lower() != 'yes':
                return

        batch = []
        for record_uid in to_restore:
            rec = deleted_records[record_uid]
            batch.append({
                'command': 'undelete_record',
                'record_uid': record_uid,
                'revision': rec['revision']
            })

        api.execute_batch(params, batch)
        TrashMixin.last_revision = 0
