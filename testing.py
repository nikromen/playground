"""
Repository wrapper for Fedora Alternative Packaging repository with
basic functionality.
"""


from os import getcwd
import pygit2
from pygit2 import Branch, Repository, clone_repository, GIT_MERGE_ANALYSIS_UP_TO_DATE, GIT_MERGE_ANALYSIS_FASTFORWARD, GIT_MERGE_ANALYSIS_NORMAL, GIT_BRANCH_REMOTE

UPSTREAM_NAME = "upstream"
ORIGIN_NAME = "origin"
UPSTREAM_REFERENCE_NAME = "refs/remotes/origin/{branch_name}"
MAIN_REFERENCE_NAME = "refs/heads/{branch_name}"



class MyRemoteCallbacks(pygit2.RemoteCallbacks):

    def credentials(self, url, username_from_url, allowed_types):
        if allowed_types & pygit2.credentials.GIT_CREDENTIAL_USERNAME:
            return pygit2.Username("git")
        elif allowed_types & pygit2.credentials.GIT_CREDENTIAL_SSH_KEY:
            return pygit2.Keypair("git", "id_rsa.pub", "id_rsa", "")
        else:
            return None


class FAPRepository(Repository):
    def __init__(self) -> None:
        self._repo_location = getcwd()
        super().__init__(path=self._repo_location)

    @staticmethod
    def clone(repo_url: str) -> bool:
        clone_repository(repo_url, getcwd())

    def _evaluate_merge_analysis(self, result: int, remote_ref: str, branch_name :str) -> None:
        if result == GIT_MERGE_ANALYSIS_UP_TO_DATE:
            return
        
        if result == GIT_MERGE_ANALYSIS_FASTFORWARD:
            self.checkout_tree(self.get(remote_ref))
            main_ref = self.lookup_reference(MAIN_REFERENCE_NAME.format(branch_name=branch_name))
            main_ref.set_target(remote_ref)
            self.head.set_target(remote_ref)
        
        if result == GIT_MERGE_ANALYSIS_NORMAL:
            return
        
        raise
    
    def pull(self, branch_name: str) -> None:
        upstream = next((remote for remote in self.remotes if remote.name == UPSTREAM_NAME), None)
        if upstream is None:
            # throw exc
            pass

        upstream.fetch(MyRemoteCallbacks())
        remote_ref = self.lookup_reference(
            UPSTREAM_REFERENCE_NAME.format(branch_name=branch_name)
        )

        result, _ = self.merge_analysis(remote_ref)
        self._evaluate_merge_analysis(result, remote_ref, branch_name)
    
    def _switch_to_branch(self, branch: Branch) -> None:
        ref = self.lookup_reference(branch.name)
        print(f"Switching to package: {branch.name}")
        self.checkout(ref)
        
    def switch(self, branch_name: str) -> bool:
        branch = self.lookup_branch(branch_name)
        if branch is not None:
            self._switch_to_branch(branch)
            return True
        
        for remote in [UPSTREAM_NAME, ORIGIN_NAME]:
            branch = self.lookup_branch('/'.join([remote, branch_name]), GIT_BRANCH_REMOTE)
            if branch is not None:
                self.pull(branch_name)
                self._switch_to_branch(branch)
                return True
        
        return False

repo = FAPRepository()
repo.switch("uwu")

