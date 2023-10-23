import subprocess
from pathlib import Path
from typing import Optional, Tuple

from tempren.exceptions import ExecutionTimeoutError, MissingMetadataError
from tempren.factories import TagFactoryFromClass
from tempren.primitives import File, Tag, TagName


class AdHocTagFactoryFromExecutable(TagFactoryFromClass):
    """Produces AdHocTag instances from given executable path"""

    _executable_path: Path

    @property
    def short_description(self) -> str:
        return self._render_description(super().short_description)

    @property
    def long_description(self) -> Optional[str]:
        long_description = super().long_description
        if long_description:
            long_description = self._render_description(long_description)
        return long_description

    def __init__(self, exec_path: Path, tag_name: TagName):
        assert exec_path.exists()
        self._executable_path = exec_path
        super().__init__(AdHocTag, tag_name)

    def __call__(self, *args, **kwargs) -> Tag:
        tag = AdHocTag(self._executable_path)
        tag.configure(*args, **kwargs)  # type: ignore
        return tag

    def _render_description(self, description: str) -> str:
        return description.format(
            executable_name=self._executable_path.name,
            executable_path=self._executable_path,
            tag_name=self.tag_name,
        )


class AdHocTag(Tag):
    """Invoke `{executable_name}` executable

    Execute `{executable_name}` and extract its output.
    If context is given, tag invocation:
        %{tag_name}("--flag", "arg"){{Context}}
    is equivalent to:
        echo "Context" | {executable_name} --flag arg

    If no context is present, tag invocation:
        %{tag_name}("--flag", "arg")
    results in equivalent command:
        {executable_name} --flag arg <relative path to the processed file>

    Program executable is located at: `{executable_path}`
    """

    executable: Path
    args: Tuple[str, ...] = ()
    timeout_ms: int = 3000

    def __init__(self, executable: Path):
        assert (
            executable.exists()
        ), "Provided executable doesn't exists in the filesystem"
        self.executable = executable

    def configure(self, *positional_args: str, timeout_ms: int = 3000):
        """
        :param positional_args: command line arguments to be passed to the executable
        :param timeout_ms: execution timeout in milliseconds
        """
        self.args = positional_args
        self.timeout_ms = timeout_ms

    def process(self, file: File, context: Optional[str]) -> str:
        if context is None:
            command_line = (
                [str(self.executable)] + list(self.args) + [str(file.relative_path)]
            )
        else:
            command_line = [str(self.executable)] + list(self.args)

        try:
            completed_process = subprocess.run(
                command_line,
                input=context.encode("utf-8") if context else None,
                capture_output=True,
                timeout=self.timeout_ms / 1000,
                cwd=file.input_directory,
            )
        except subprocess.TimeoutExpired:
            raise ExecutionTimeoutError(
                "`{}` command execution exceeded timeout {}ms".format(
                    " ".join(command_line), self.timeout_ms
                )
            )

        captured_stdout = completed_process.stdout.decode("utf-8")
        if completed_process.returncode != 0:
            captured_stderr = completed_process.stderr.decode("utf-8")
            raise MissingMetadataError(
                "Command failed due to error code ({}): \n{}".format(
                    completed_process.returncode, captured_stderr
                )
            )
        return captured_stdout.strip()
