import io
import os
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Tuple

import pytest

import tempren.cli

ErrorCode = tempren.cli.ErrorCode
project_root_path = os.getcwd()

# Both tests and tempren process manipulate CurrentWorkingDirectory setting.
# Following environment allows for running tempren out of the main repository directory.
tempren_process_env = os.environ.copy()
tempren_process_env["PYTHONPATH"] = ":".join(
    [project_root_path, tempren_process_env.get("PYTHONPATH", "")]
)


def run_tempren_process(*args) -> Tuple[str, str, int]:
    """Run tempren with provided arguments as separate process"""
    args = list(map(str, filter(lambda v: v is not None, args)))
    print("CWD:", os.getcwd())
    print("COMMAND: tempren", " ".join(args))
    completed_process = subprocess.run(
        [sys.executable, "-m", "tempren.cli"] + args,
        capture_output=True,
        env=tempren_process_env,
    )

    captured_stdout = completed_process.stdout.decode("utf-8")
    print("STDOUT:\n" + captured_stdout)
    captured_stderr = completed_process.stderr.decode("utf-8")
    print("STDERR:\n" + captured_stderr)
    return (
        captured_stdout,
        captured_stderr,
        completed_process.returncode,
    )


def start_tempren_process(*args) -> subprocess.Popen:
    """Run tempren with provided arguments as separate process"""
    args = list(map(str, filter(lambda v: v is not None, args)))
    # CHECK: Use pexpect?
    # print("Running: tempren", " ".join(args))
    tempren_process = subprocess.Popen(
        [sys.executable, "-m", "tempren.cli"] + args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=tempren_process_env,
        bufsize=1,
        universal_newlines=True,
    )
    return tempren_process


def run_tempren(*args) -> Tuple[str, str, int]:
    """Run tempren's main() function with provided arguments"""
    args = list(map(str, filter(lambda v: v is not None, args)))
    old_sys_argv = sys.argv.copy()
    sys.argv[1:] = args
    print("Running: tempren", " ".join(args))
    try:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                error_code = tempren.cli.main()
    finally:
        sys.argv = old_sys_argv

    return stdout.getvalue(), stderr.getvalue(), error_code


def make_relative(path: Path) -> Path:
    os.chdir(path.parent)
    cwd = os.getcwd()
    return path.relative_to(cwd)


@pytest.mark.e2e
class CliTestsBase:
    pass
