# -*- coding: utf-8 -*-

import re
from getpass import getuser

from six.moves.urllib.parse import urlencode

import codecli.utils as utils
from codecli.providers.base import GitServiceProvider


class CodeProvider(GitServiceProvider):
    URLS = ['https://msasg.visualstudio.com']

    def send_pullreq(self, head_repo, head_ref, base_repo, base_ref):
        url = "https://msasg.visualstudio.com/DefaultCollection/%s/pullrequestcreate?sourceRef=%s&targetRef=%s" % (
            base_repo, head_ref, base_ref)
        utils.print_log("goto " + url)
        utils.browser_open(url)


    def get_remote_repo_name(self, remote):
        repourl = self.get_remote_repo_url(remote)
        _, _, reponame = repourl.partition('visualstudio.com/DefaultCollection/')
        return reponame

    def get_remote_repo_url(self, remote):
        for line in utils.getoutput(['git', 'remote', '-v']).splitlines():
            words = line.split()
            if words[0] == remote and words[-1] == '(push)':
                giturl = words[1]
                break
        else:
            raise Exception("no remote %s found" % remote)

        giturl = re.sub(r"(?<=https://).+:.+@", "", giturl)
        assert re.match(r"^https://\w+.visualstudio.com/DefaultCollection/[a-zA-Z0-9_-]+/_git/[a-zA-Z0-9_-]+", giturl), \
            "This url do not look like VSOnline git repo url: %s" % giturl
        return giturl

    def get_repo_git_url(self, repo_name, login_user=''):
        if '://' in repo_name:
            return repo_name

        return 'https://msasg.visualstudio.com/DefaultCollection/%s' % repo_name

    def get_username(self):
        email = utils.get_config('user.email')
        return email.split('@')[0] if email and email.endswith('@microsoft.com') else None

    def merge_config(self):
        email = utils.get_config('user.email')
        if not email:
            email = utils.getoutput(['git', 'config', 'user.email']).strip()
            if not email.endswith('@microsoft.com'):
                email = '%s@microsoft.com' % getuser()
            email = utils.ask(
                "Please enter your @microsoft.com email [%s]: " % email,
                default=email)
            utils.set_config('user.email', email)

        name = utils.get_user_name()
        if not name:
            name = email.split('@')[0]
            name = utils.ask("Please enter your name [%s]: " % name, default=name)
            utils.set_config('user.name', name)

        for key, value in utils.iter_config():
            utils.check_call(['git', 'config', key, value])
