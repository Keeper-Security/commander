import tempfile
import json
import os
import shutil
import warnings

from unittest import TestCase, mock

from data_config import read_config_file
from keepercommander.params import KeeperParams
from keepercommander import cli, api
from keepercommander.subfolder import BaseFolderNode


class TestConnectedCommands(TestCase):
    params = None

    @classmethod
    def setUpClass(cls):
        cls.params = KeeperParams()
        read_config_file(cls.params)
        api.login(cls.params)
        TestConnectedCommands.wipe_out_data()

    @classmethod
    def tearDownClass(cls):
        cli.do_command(cls.params, 'logout')

    @classmethod
    def wipe_out_data(cls):
        params = cls.params    # type: KeeperParams

        params.revision = 0
        api.sync_down(params)
        request = {
            'command': 'record_update',
            'delete_records': [key for key in params.record_cache.keys()]
        }
        api.communicate(params, request)

        for shared_folder_uid in params.shared_folder_cache:
            request = {
                'command': 'shared_folder_update',
                'operation': 'delete',
                'shared_folder_uid': shared_folder_uid
            }
            api.communicate(params, request)

        folder_uids = [x for x in params.root_folder.subfolders if params.subfolder_cache[x]['type'] == BaseFolderNode.UserFolderType]
        if folder_uids:
            request = {
                'command': 'pre_delete',
                'objects': [
                    {
                        'from_type': 'user_folder',
                        'object_uid': x,
                        'object_type': 'user_folder',
                        'delete_resolution': 'unlink'
                    } for x in folder_uids
                ]
            }
            rs = api.communicate(params, request)
            request = {
                'command': 'delete',
                'pre_delete_token': rs['pre_delete_response']['pre_delete_token']
            }
            api.communicate(params, request)

        request = {
            'command': 'purge_deleted_records'
        }
        api.communicate(params, request)
        params.revision = 0
        api.sync_down(params)

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        # Windows doesn't play nice with temp files, so create tmpdir that may fail to delete
        self.tmpdir = os.path.join(os.path.dirname(__file__), 'tmp')
        os.makedirs(self.tmpdir, exist_ok=True)
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

    def test_commands(self):
        params = TestConnectedCommands.params # type: KeeperParams
        with mock.patch('builtins.input', side_effect = KeyboardInterrupt()), mock.patch('builtins.print'):
            record_uid = cli.do_command(params, 'add  --login="user@keepersecurity.com" --pass=password --url="https://keepersecurity.com/" --custom="{\\"cmdr:plugin\\":\\"noop\\"}" --title="Record 1"')
            cli.do_command(params, 'sync-down')

            rec = api.get_record(params, record_uid)

            self.assertEqual(rec.get('cmdr:plugin'), 'noop')
            old_password = rec.password
            cli.do_command(params, 'rotate -- {0}'.format(rec.record_uid))
            cli.do_command(params, 'sync-down')
            rec = api.get_record(params, record_uid)
            self.assertNotEqual(old_password, rec.password)

            cli.do_command(params, 'ls -l')
            cli.do_command(params, 'mkdir --user-folder "User Folder 1"')
            cli.do_command(params, 'mkdir --shared-folder --all "Shared Folder 1"')
            cli.do_command(params, 'sync-down')
            cli.do_command(params, 'cd "User Folder 1"')
            cli.do_command(params, 'mkdir --user-folder "User Folder 2"')
            cli.do_command(params, 'cd /')
            cli.do_command(params, 'ln "Record 1" "Shared Folder 1"')
            cli.do_command(params, 'mv "Record 1" "User Folder 1"')
            params.revision = 0
            cli.do_command(params, 'sync-down')
            self.assertEqual(len(params.record_cache), 1)
            self.assertEqual(len(params.shared_folder_cache), 1)

            cli.do_command(params, 'cd "Shared Folder 1"')
            cli.do_command(params, 'append-notes --notes="Additional info" "Record 1"')
            cli.do_command(params, 'sync-down')
            cli.do_command(params, 'cd "../User Folder 1"')
            cli.do_command(params, 'rmdir --force "User Folder 2"')
            cli.do_command(params, 'sync-down')

            cli.do_command(params, 'cd /')
            cli.do_command(params, 'search record')
            cli.do_command(params, 'search folder')

            with tempfile.NamedTemporaryFile(dir=self.tmpdir, delete=False) as f:
                f.write(b'data')
                f.flush()
                cli.do_command(params, 'cd "User Folder 1"')
                cli.do_command(params, 'upload-attachment --file="{0}" "Record 1"'.format(f.name))
            cli.do_command(params, 'sync-down')

            rec = api.get_record(params, record_uid)
            self.assertEqual(len(rec.attachments), 1)
            cli.do_command(params, 'delete-attachment --name={0} -- {1}'.format(rec.attachments[0]['id'], record_uid))
            cli.do_command(params, 'sync-down')
            rec = api.get_record(params, record_uid)
            self.assertEqual(len(rec.attachments), 0)

            script_path = os.path.dirname(__file__)
            cwd = os.getcwd()
            if script_path.startswith(cwd):
                script_path = script_path[len(cwd):]
                if script_path.startswith(os.sep):
                    script_path = script_path[1:]
            file = 'keepass.kdbx'
            if script_path:
                file = os.path.join(script_path, file)
            if os.path.isfile(file):
                os.remove(file)

            with mock.patch('getpass.getpass', return_value='password'):
                cli.do_command(params, 'export --format=keepass "{0}"'.format(file))

            TestConnectedCommands.wipe_out_data()
            cli.do_command(params, 'sync-down')

            with mock.patch('getpass.getpass', return_value='password'), mock.patch('builtins.input', return_value=''):
                cli.do_command(params, 'import --format=keepass "{0}"'.format(file))
            cli.do_command(params, 'sync-down')

            json_text = ''
            with mock.patch('builtins.open', mock.mock_open()) as m_open, mock.patch('os.path.abspath', return_value='file/path'):
                def file_write(text):
                    nonlocal json_text
                    json_text += text

                m_open.return_value.write = file_write
                cli.do_command(params, 'export --format=json file')
            self.assertTrue(len(json_text) > 0)
            exported = json.loads(json_text)
            self.assertEqual(len(params.record_cache), len(exported['records']))
            self.assertEqual(len(params.shared_folder_cache), len(exported['shared_folders']))

            TestConnectedCommands.wipe_out_data()
            with mock.patch('builtins.open', mock.mock_open()) as m_open, mock.patch('os.path.isfile', return_value=True):
                def file_read():
                    nonlocal json_text
                    return json_text

                m_open.return_value.read = file_read
                cli.do_command(params, 'import --format=json file')

            self.assertEqual(len(params.record_cache), len(exported['records']))
            self.assertEqual(len(params.shared_folder_cache), len(exported['shared_folders']))
