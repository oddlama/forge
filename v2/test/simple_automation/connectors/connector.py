"""
Defines the connector interface.
"""

from __future__ import annotations

from typing import Callable, Optional, Union
from simple_automation.types import HostType

class CompletedRemoteCommand:
    """
    The return value of run(), representing a finished remote process.
    """
    def __init__(self, stdout: Optional[bytes], stderr: Optional[bytes], returncode: int):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

class StatResult:
    """
    The return value of stat(), representing information about a remote file.
    The type will be one of [ "dir", "chr", "blk", "file", "fifo", "link", "sock", "other" ]
    """
    def __init__(self,
                 type: str, # pylint: disable=redefined-builtin
                 mode: Union[int, str],
                 owner: str,
                 group: str,
                 size: int,
                 mtime: int,
                 ctime: int):
        self.type = type
        self.mode: str = mode if isinstance(mode, str) else oct(mode)[2:]
        self.owner = owner
        self.group = group
        self.size = size
        self.mtime = mtime
        self.ctime = ctime

class Connector:
    """
    The base class for all connectors.
    """

    schema: str
    """
    The schema of the connector. Must match the schema used in urls of this connector,
    such as `ssh` for `ssh://...`. May also be shown in messages like:

        "Establishing connecting to {host} via {schema}"

    Overwrite this in your connector subclass. Must be unique among all connectors.
    """

    registered_connectors: dict[str, Callable[[str, HostType], Connector]] = {}
    """
    The list of all registered connectors.
    """

    def __init__(self, url: Optional[str], host: HostType):
        self.url = url
        self.host = host

    def open(self) -> None:
        """
        Opens the connection to the remote host.
        """
        raise NotImplementedError("Must be overwritten by subclass.")

    def close(self) -> None:
        """
        Closes the connection to the remote host.
        """
        raise NotImplementedError("Must be overwritten by subclass.")

    def run(self,
            command: list[str],
            input: Optional[bytes] = None, # pylint: disable=redefined-builtin
            capture_output: bool = True,
            check: bool = True,
            user: Optional[str] = None,
            group: Optional[str] = None,
            umask: Optional[str] = None,
            cwd: Optional[str] = None) -> CompletedRemoteCommand:
        """
        Runs the given command on the remote, returning a CompletedRemoteCommand
        containing the returned information (if any) and the status code.

        Raises a ValueError if the command cannot be run for various reasons (e.g.
        the specified user does not exist, the cwd does not exist, ...).

        Parameters
        ----------
        command
            The command to be executed on the remote host.
        input
            Input to the remote command.
        capture_output
            Whether the output of the command should be captured.
        check
            Whether to raise an exception if the remote command returns with a non-zero exit status.
        user
            The remote user under which the command should be run. Also sets the group
            to the primary group of that user if it isn't explicitly given. If not given, the command
            is run as the user under which the remote dispatcher is running (usually root).
        group
            The remote group under which the command should be run. If not given, the command
            is run as the group under which the remote dispatcher is running (usually root),
            or in case the user was explicitly specified, the primary group of that user.
        umask
            The umask to use when executing the command on the remote system. Defaults to "077".
        cwd
            The remote working directory under which the command should be run.

        Returns
        -------
        CompletedRemoteCommand
            The result of the remote command.
        """
        raise NotImplementedError("Must be overwritten by subclass.")

    def resolve_user(self, user: Optional[str]) -> Optional[str]:
        """
        Resolves the given user (if not None) on the remote, returning
        the canonicalized username.

        Raises a ValueError if the user doesn't exist.

        Parameters
        ----------
        user
            The username or uid that should be resolved.

        Returns
        -------
        Optional[str]
            The resolved username or None if the input was None.
        """
        raise NotImplementedError("Must be overwritten by subclass.")

    def resolve_group(self, group: Optional[str]) -> Optional[str]:
        """
        Resolves the given group (if not None) on the remote, returning
        the canonicalized groupname.

        Raises a ValueError if the group doesn't exist.

        Parameters
        ----------
        group
            The groupname or gid that should be resolved.

        Returns
        -------
        Optional[str]
            The resolved groupname or None if the input was None.
        """
        raise NotImplementedError("Must be overwritten by subclass.")

    def stat(self, path: str, follow_links: bool = False) -> Optional[StatResult]:
        """
        Runs stat() on the given path on the remote. Follows links if follow_links
        is true.

        Returns None if the remote couldn't stat the given path.

        Parameters
        ----------
        path
            The path to stat.
        follow_links
            Whether to follow symbolic links instead of running stat on the link.

        Returns
        -------
        Optional[StatResult]
            The resolved groupname or None if the input was None.
        """
        raise NotImplementedError("Must be overwritten by subclass.")

def connector(cls):
    """
    The @connector class decorator used to register the connector
    to the global registry.
    """
    if not hasattr(cls, 'schema'):
        raise RuntimeError(f"{cls.__name__} was decorated with @connector but is not exposing a '{cls.__name__}.schema' attribute.")
    Connector.registered_connectors[cls.schema] = cls
    return cls
