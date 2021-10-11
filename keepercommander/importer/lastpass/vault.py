# coding: utf-8
import os
import shutil
from tempfile import mkdtemp

from . import fetcher
from . import parser
from .exceptions import InvalidResponseError
from .shared_folder import LastpassSharedFolder


class Vault(object):
    @classmethod
    def open_remote(cls, username, password, multifactor_password=None, client_id=None, **kwargs):
        """Fetches a blob from the server and creates a vault"""
        session = fetcher.login(username, password, multifactor_password, client_id)
        blob = fetcher.fetch(session)
        encryption_key = blob.encryption_key(username, password)
        vault = cls(blob, encryption_key, session, kwargs.get('tmpdir'), kwargs.get('users_only') or False)

        fetcher.logout(session)
        return vault

    @classmethod
    def open_local(cls, blob_filename, username, password):
        """Creates a vault from a locally stored blob"""
        # TODO: read the blob here
        raise NotImplementedError()

    def __init__(self, blob, encryption_key, session, tmpdir, shared_folder_details):
        """This more of an internal method, use one of the static constructors instead"""
        chunks = parser.extract_chunks(blob)

        if not self.is_complete(chunks):
            raise InvalidResponseError('Blob is truncated')

        self.errors = set()
        self.shared_folders = []
        self.attachments = []
        self.accounts = self.parse_accounts(chunks, encryption_key)

        self.process_attachments(session, tmpdir)

        try:
            if self.shared_folders and shared_folder_details:
                for shared_folder in self.shared_folders:
                    members, teams, error = fetcher.fetch_shared_folder_members(session, shared_folder.id)
                    if error:
                        self.errors.add(error)
                        break
                    else:
                        shared_folder.members = members
                        shared_folder.teams = teams
        except:
            pass

    def is_complete(self, chunks):
        return len(chunks) > 0 and chunks[-1].id == b'ENDM' and chunks[-1].payload == b'OK'

    def parse_accounts(self, chunks, encryption_key):
        accounts = []

        key = encryption_key
        rsa_private_key = None
        shared_folder = None

        for i in chunks:
            if i.id == b'ACCT':
                account = parser.parse_ACCT(i, key, shared_folder)
                if account:
                    accounts.append(account)
            elif i.id == b'PRIK':
                rsa_private_key = parser.parse_PRIK(i, encryption_key)
            elif i.id == b'SHAR':
                # After SHAR chunk all the folliwing accounts are enrypted with a new key
                share = parser.parse_SHAR(i, encryption_key, rsa_private_key)
                key = share['encryption_key']
                shareid = share['id'].decode('utf-8')
                shared_folder = LastpassSharedFolder(shareid, share['name'].decode('utf-8'))
                self.shared_folders.append(shared_folder)
            elif i.id == b'ATTA':
                attachment = parser.parse_ATTA(i, accounts)
                if attachment:
                    self.attachments.append(attachment)

        return accounts

    def process_attachments(self, session, tmpdir=None):
        attach_cnt = len(self.attachments)
        if attach_cnt > 0:
            attach_cnt_digits = len(str(attach_cnt))
            if tmpdir is None:
                tmpdir = mkdtemp()
            else:
                tmpdir = os.path.abspath(tmpdir)
                if not os.path.exists(tmpdir):
                    os.makedirs(tmpdir)

        for i, attachment in enumerate(self.attachments):
            tmp_filename = f'{str(i).zfill(attach_cnt_digits)}of{attach_cnt}_{attachment.file_id}'
            attachment.tmpfile = os.path.join(tmpdir, tmp_filename)
            with fetcher.stream_attachment(session, attachment) as r:
                with open(attachment.tmpfile, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
