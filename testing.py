import pygit2
import os
from pygit2 import GIT_BRANCH_ALL, GIT_BRANCH_REMOTE


cwd = os.getcwd()
repo_path = pygit2.discover_repository(cwd)
repo = pygit2.Repository(repo_path)
branch = repo.lookup_branch("uwu", GIT_BRANCH_ALL)
branches = repo.raw_listall_branches(GIT_BRANCH_ALL)
ref = repo.lookup_reference(branch.name)
repo.checkout(ref)

a = 2

