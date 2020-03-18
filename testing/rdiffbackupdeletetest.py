import os
import sys

from commontest import old_test_dir, abs_test_dir
from distutils import spawn
import subprocess
import unittest

PY2 = sys.version_info < (3,)
PY3 = sys.version_info > (3,)


# Lookup for rdiff-backup-delete location.
def rdiff_backup_delete(to_delete=None, extra_args=[], expected_ret_val=0, expected_output=None):
    bin = spawn.find_executable(u"rdiff-backup-delete")
    assert bin, "can't find rdiff-backup-delete"
    cmdargs = [bin.encode('utf8')]
    if extra_args:
        cmdargs.extend(extra_args)
    if to_delete:
        cmdargs.append(to_delete)
    cmdline = b" ".join(cmdargs)
    print("Executing: %r" % (cmdline,))
    p = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()
    ret_val = p.poll()
    if expected_ret_val is not None:
        assert ret_val == expected_ret_val, "Return code %d of command '%s' doesn't match expected value: %d.\n%s\n%s" % \
            (ret_val, cmdline, expected_ret_val, output, error)
    if expected_output is not None:
        assert expected_output in output or expected_output in error, "Output %s %s of command '%s' doesn't match expected output:\n'%s'" % \
            (output, error, cmdline, expected_output)


def rdiff_backup_verify(backup_dir):
    assert backup_dir
    assert os.path.isdir(backup_dir)

    # Lookup rdiff-backup executable.
    bin = spawn.find_executable("rdiff-backup")
    assert bin, "can't find rdiff-backup"

    # Build the command line
    cmdargs = [bin.encode('utf8'), b'--verify', backup_dir]
    cmdline = b" ".join(cmdargs)
    print("Executing: %r" % (cmdline,))
    DEVNULL = open(os.devnull, 'wb')
    try:
        p = subprocess.Popen(cmdargs, stdout=DEVNULL, stderr=DEVNULL)
        assert p.wait() == 0, 'rdiff-backup verify failed'
    finally:
        DEVNULL.close()


class RdiffBackupDeleteTest(unittest.TestCase):

    repo = ""

    def _copy_repo(self, reponame):
        # Copy the required repo to a temporary location.
        # We need to use os command line to properly copy and delete special files.
        self.repo = os.path.join(abs_test_dir, b'/tmp/deletetest')
        if os.path.exists(self.repo):
            subprocess.check_call([b'rm', b'-Rf', self.repo])
        src = os.path.join(old_test_dir, reponame)
        subprocess.check_call([b'cp', b'-R', src, self.repo])

    def _find(self, search):
        for root, dirs, files in os.walk(self.repo):
            for name in files:
                if search in name:
                    yield os.path.join(root, name)
            for name in dirs:
                if search in name:
                    yield os.path.join(root, name)

    def assertFound(self, search):
        found = list(self._find(search))
        assert found, "%r can't be found" % (search,)

    def assertNotFound(self, search):
        found = list(self._find(search))
        assert not found, "%r should not be found" % (found,)

    def tearDown(self):
        if os.path.exists(self.repo):
            subprocess.check_call(['rm', '-Rf', self.repo])

    def test_arguments(self):
        # Call with --help or -h should return 0 and print the usage.
        rdiff_backup_delete(extra_args=[b'--help'],
                            expected_output=b'Usage:')
        rdiff_backup_delete(extra_args=[b'-h'],
                            expected_output=b'Usage:')
        # Call without arguments
        rdiff_backup_delete(extra_args=[], expected_ret_val=1,
                            expected_output=b'fatal: missing arguments')
        # Call with invalid arguments
        rdiff_backup_delete(extra_args=[b'--invalid'], expected_ret_val=1,
                            expected_output=b'fatal: bad command line: option --invalid not recognized')

    def test_rdiff_backup_dir(self):
        # without rdiff-backup-dir
        rdiff_backup_delete(to_delete=b'somefile', expected_ret_val=1,
                            expected_output=b'fatal: not a rdiff-backup repository (or any parent up to mount point /)')

    def test_delete_with_file(self):
        self._copy_repo(b'restoretest4')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'tmp/changed'))
        rdiff_backup_verify(self.repo)
        self.assertNotFound(b'changed')

    def test_delete_with_directory(self):
        self._copy_repo(b'restoretest4')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'tmp'))
        rdiff_backup_verify(self.repo)
        self.assertNotFound(b'tmp')

    def test_delete_with_deleted_directory(self):
        self._copy_repo(b'restoretest3')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'increment1'))
        rdiff_backup_verify(self.repo)
        self.assertNotFound(b'increment1')

    def test_delete_with_symlink(self):
        self._copy_repo(b'restoretest3')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'various_file_types/symbolic_link'))
        rdiff_backup_verify(self.repo)
        self.assertNotFound(b'symbolic_link')

    def test_delete_with_hardlink(self):
        self._copy_repo(b'restoretest3')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'various_file_types/two_hardlinked_files1'))
        rdiff_backup_verify(self.repo)
        self.assertNotFound(b'two_hardlinked_files1')

    def test_delete_with_fifo(self):
        self._copy_repo(b'restoretest5')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'fifo'))
        rdiff_backup_verify(self.repo)
        self.assertNotFound(b'fifo')

    def test_delete_with_non_utf8(self):
        self._copy_repo(b'restoretest5')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'various_file_types/\xd8\xab\xb1Wb\xae\xc5]\x8a\xbb\x15v*\xf4\x0f!\xf9>\xe2Y\x86\xbb\xab\xdbp\xb0\x84\x13k\x1d\xc2\xf1\xf5e\xa5U\x82\x9aUV\xa0\xf4\xdf4\xba\xfdX\x03\x82\x07s\xce\x9e\x8b\xb34\x04\x9f\x17 \xf4\x8f\xa6\xfa\x97\xab\xd8\xac\xda\x85\xdcKvC\xfa#\x94\x92\x9e\xc9\xb7\xc3_\x0f\x84g\x9aB\x11<=^\xdbM\x13\x96c\x8b\xa7|*"\\\'^$@#!(){}?+ ~` '))
        rdiff_backup_verify(self.repo)

    def test_delete_access_control_lists(self):
        self._copy_repo(b'restoretest3')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'increment1'))
        rdiff_backup_verify(self.repo)
        self.assertNotFound(b'increment1')

    def test_extended_attributes(self):
        self._copy_repo(b'restoretest3')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'newdir2'))
        rdiff_backup_verify(self.repo)
        self.assertNotFound(b'newdir2')

    def test_delete_with_dryrun(self):
        self._copy_repo(b'restoretest4')
        rdiff_backup_delete(to_delete=os.path.join(self.repo, b'tmp'), extra_args=[b'--dry-run'])
        rdiff_backup_verify(self.repo)
        self.assertFound(b'tmp')


if __name__ == "__main__":
    unittest.main()
