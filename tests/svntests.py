#!/usr/bin/env python

import os
import re
import textwrap

from gitsvntests import GitSvnTests
from svnfixtures import SvnFixtures
from utils       import run_svn


class SvnTests(GitSvnTests):

    """Unit tests for 'tar_scm --scm svn'.

    svn-specific tests are in this class.  Other shared tests are
    included via the class inheritance hierarchy.
    """

    scm = 'svn'
    initial_clone_command = 'svn (co|checkout) '
    update_cache_command  = 'svn up(date)?'
    sslverify_false_args  = '--trust-server-cert'
    fixtures_class = SvnFixtures

    def default_version(self):
        return self.rev(2)

    def changesrevision(self, rev, abbrev=False):
        return rev

    def changesregex(self, rev):
        return rev

    def tar_scm_args(self):
        scm_args = [
            '--changesgenerate', 'enable',
            '--versionformat', '0.6.%r',
        ]
        return scm_args

    def test_versionformat_rev(self):
        self.tar_scm_std('--versionformat', 'myrev%r.svn')
        self.assertTarOnly(self.basename(version='myrev2.svn'))

    def test_version_versionformat(self):
        self.tar_scm_std('--version', '3.0', '--versionformat', 'myrev%r.svn')
        self.assertTarOnly(self.basename(version='myrev2.svn'))

    def test_versionformat_revision(self):
        self.fixtures.create_commits(4)
        self.tar_scm_std('--versionformat', 'foo%r', '--revision', self.rev(2))
        basename = self.basename(version='foo2')
        th = self.assertTarOnly(basename)
        self.assertTarMemberContains(th, basename + '/a', '2')

    def _check_servicedata(self, expected_dirents=2, revision=2):
        dirents = self.assertNumDirents(self.outdir, expected_dirents)
        self.assertTrue('_servicedata' in dirents,
                        '_servicedata in %s' % repr(dirents))
        sd = open(os.path.join(self.outdir, '_servicedata')).read()
        expected = (
            r"<servicedata>"
            r"\s*<service name=\"tar_scm\">"
            r"\s*<param name=\"url\">%s</param>"
            r"\s*<param name=\"changesrevision\">([0-9].*)</param>"
            r"\s*</service>"
            r"\s*</servicedata>" % self.fixtures.repo_url
        )
        m = re.match(expected, sd)
        if m:
            print("matched")
        else:
            print("matched not")
        self.assertTrue(m, "\n'%s'\n!~ /%s/" % (sd, expected))
