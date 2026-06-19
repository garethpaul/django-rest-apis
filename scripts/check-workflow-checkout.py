#!/usr/bin/env python3
import _hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


CANONICAL_WORKFLOW_ENTRIES = {
    ".github/workflows": "directory",
    ".github/workflows/check.yml": "file",
}
CANONICAL_WORKFLOW_HASHES = {
    ".github/workflows/check.yml": (
        "f5cdeb4df78224823a02eeade8a74f75dc0110b0dc0b6e75d6577fa09400a2e2"
    ),
}
CANONICAL_LOCAL_ACTION_ENTRIES = {}
CANONICAL_LOCAL_ACTION_HASHES = {}
CANONICAL_REPOSITORY_FILES = {
    "Makefile": "eff83ef67a609d2f647f65458e462d239a7ec593d96eff24687d4252a6657e5d",
}
MAKE_SHADOW_NAMES = ("GNUmakefile", "makefile")
MAKE_ENVIRONMENT_VARIABLES = (
    "MAKEFILES",
    "MAKEFLAGS",
    "MFLAGS",
    "GNUMAKEFLAGS",
)


def sha256(path):
    digest = _hashlib.openssl_sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value):
    return _hashlib.openssl_sha256(value).hexdigest()


def relative_path(repository, path):
    return path.relative_to(repository).as_posix()


def entry_type(mode):
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISLNK(mode):
        return "symlink"
    return "non-regular"


def inventory_tree(repository, relative_root, label, required):
    root = repository / relative_root
    try:
        root_mode = os.lstat(root).st_mode
    except FileNotFoundError:
        if required:
            raise ValueError("GitHub Actions {} root is missing: {}.".format(label, relative_root))
        return {}

    root_type = entry_type(root_mode)
    if root_type != "directory":
        raise ValueError(
            "GitHub Actions {} root must be a real directory, not {}: {}.".format(
                label, root_type, relative_root
            )
        )

    inventory = {relative_root: "directory"}
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            children = sorted(entries, key=lambda entry: entry.name, reverse=True)
        for child in children:
            path = Path(child.path)
            relative = relative_path(repository, path)
            kind = entry_type(os.lstat(path).st_mode)
            if kind == "symlink":
                raise ValueError(
                    "GitHub Actions {} tree contains symlink: {}.".format(label, relative)
                )
            if kind == "non-regular":
                raise ValueError(
                    "GitHub Actions {} tree contains non-regular entry: {}.".format(
                        label, relative
                    )
                )
            inventory[relative] = kind
            if kind == "directory":
                pending.append(path)
    return inventory


def validate_inventory(actual, expected, label):
    if actual == expected:
        return None

    actual_paths = set(actual)
    expected_paths = set(expected)
    added = sorted(actual_paths - expected_paths)
    missing = sorted(expected_paths - actual_paths)
    changed = sorted(
        path
        for path in actual_paths & expected_paths
        if actual[path] != expected[path]
    )
    details = []
    if added:
        details.append("added {}".format(", ".join(added)))
    if missing:
        details.append("missing {}".format(", ".join(missing)))
    if changed:
        details.append(
            "changed types {}".format(
                ", ".join(
                    "{} (expected {}, got {})".format(
                        path, expected[path], actual[path]
                    )
                    for path in changed
                )
            )
        )
    return "GitHub Actions {} inventory mismatch: {}.".format(
        label, "; ".join(details)
    )


def validate_hashes(repository, expected, label):
    for relative in sorted(expected):
        path = repository / relative
        actual_digest = sha256(path)
        expected_digest = expected[relative]
        if actual_digest != expected_digest:
            return "{} SHA-256 mismatch for {}: expected {}, got {}.".format(
                label, relative, expected_digest, actual_digest
            )
    return None


def validate_repository_files(repository):
    for relative in sorted(CANONICAL_REPOSITORY_FILES):
        path = repository / relative
        try:
            kind = entry_type(os.lstat(path).st_mode)
        except FileNotFoundError:
            return "Canonical repository file is missing: {}.".format(relative)
        if kind != "file":
            return "Canonical repository file must be regular, not {}: {}.".format(
                kind, relative
            )
    return validate_hashes(
        repository, CANONICAL_REPOSITORY_FILES, "Makefile"
    )


def find_make_shadows(repository):
    shadows = []
    for directory, directory_names, filenames in os.walk(repository, topdown=True):
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name not in (".git", "__pycache__")
        )
        for filename in sorted(filenames):
            if filename in MAKE_SHADOW_NAMES:
                shadows.append(relative_path(repository, Path(directory) / filename))
    return shadows


def validate_make_inputs(repository):
    for variable in MAKE_ENVIRONMENT_VARIABLES:
        if os.environ.get(variable):
            return "{} must be unset during canonical verification.".format(variable)
    shadows = find_make_shadows(repository)
    if shadows:
        return "Make shadow files are forbidden: {}.".format(", ".join(shadows))
    return None


def validate(repository):
    try:
        workflows = inventory_tree(
            repository, ".github/workflows", "workflow", required=True
        )
        local_actions = inventory_tree(
            repository, ".github/actions", "local action", required=False
        )
    except (OSError, ValueError) as error:
        return str(error)

    checks = (
        lambda: validate_inventory(
            workflows, CANONICAL_WORKFLOW_ENTRIES, "workflow"
        ),
        lambda: validate_hashes(
            repository, CANONICAL_WORKFLOW_HASHES, "GitHub Actions workflow"
        ),
        lambda: validate_inventory(
            local_actions, CANONICAL_LOCAL_ACTION_ENTRIES, "local action"
        ),
        lambda: validate_hashes(
            repository, CANONICAL_LOCAL_ACTION_HASHES, "GitHub Actions local action"
        ),
        lambda: validate_repository_files(repository),
        lambda: validate_make_inputs(repository),
    )
    for check in checks:
        error = check()
        if error:
            return error
    return None


def run_git(repository, arguments):
    git = os.environ.get("TRUSTED_GIT")
    if not git or not Path(git).is_absolute():
        raise ValueError("TRUSTED_GIT must name a verified absolute executable.")
    result = subprocess.run(
        [git, "-C", str(repository), *arguments],
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(
            "git {} failed: {}".format(
                " ".join(arguments), result.stderr.decode("utf-8", "replace").strip()
            )
        )
    return result.stdout


def validate_trusted_executable(path):
    executable = Path(path)
    if not executable.is_absolute():
        return "Trusted executable path must be absolute: {}.".format(path)
    try:
        resolved = executable.resolve(strict=True)
    except OSError as error:
        return "Trusted executable cannot be resolved: {}: {}.".format(path, error)
    if resolved != executable:
        return "Trusted executable must use its resolved path: {} -> {}.".format(
            executable, resolved
        )
    current = executable
    while True:
        details = os.lstat(current)
        if current == executable and not stat.S_ISREG(details.st_mode):
            return "Trusted executable must be a regular file: {}.".format(executable)
        if details.st_uid != 0 or details.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            return "Trusted executable path must be root-owned and immutable: {}.".format(
                current
            )
        if current.parent == current:
            break
        current = current.parent
    if not os.access(executable, os.X_OK):
        return "Trusted executable is not executable: {}.".format(executable)
    return None


def validate_trusted_tools(paths):
    for path in paths:
        error = validate_trusted_executable(path)
        if error:
            return error
    return None


def require_clean_tracked_tree(repository):
    status = run_git(
        repository, ["status", "--porcelain=v1", "--untracked-files=all"]
    )
    if status:
        raise ValueError(
            "Tracked-tree snapshot requires a clean repository: {}".format(
                status.decode("utf-8", "replace").strip()
            )
        )


def tracked_paths(repository):
    output = run_git(repository, ["ls-files", "-z"])
    return [Path(value.decode("utf-8")) for value in output.split(b"\0") if value]


def tracked_snapshot(repository):
    files = {}
    for relative in tracked_paths(repository):
        path = repository / relative
        kind = entry_type(os.lstat(path).st_mode)
        if kind != "file":
            raise ValueError(
                "Tracked-tree entries must be regular files, not {}: {}.".format(
                    kind, relative.as_posix()
                )
            )
        mode = stat.S_IMODE(os.lstat(path).st_mode)
        files[relative.as_posix()] = {"sha256": sha256(path), "mode": mode}
    baseline = files.get("scripts/check-baseline.sh")
    if not baseline or not baseline["mode"] & stat.S_IXUSR:
        raise ValueError(
            "scripts/check-baseline.sh must retain tracked executable mode."
        )
    return {
        "files": files,
        "index": sha256_bytes(run_git(repository, ["ls-files", "-s", "-z"])),
        "tree": run_git(repository, ["rev-parse", "HEAD^{tree}"])
        .decode("ascii")
        .strip(),
    }


def copy_snapshot(repository, destination, snapshot):
    if destination.exists():
        shutil.rmtree(destination)
    for copy_name in ("tests", "verifier"):
        copy_root = destination / copy_name / "repository"
        copy_root.mkdir(parents=True)
        for relative in sorted(snapshot["files"]):
            source = repository / relative
            target = copy_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            os.chmod(target, snapshot["files"][relative]["mode"])
        copied = {}
        for relative in snapshot["files"]:
            target = copy_root / relative
            copied[relative] = {
                "sha256": sha256(target),
                "mode": stat.S_IMODE(os.lstat(target).st_mode),
            }
        if copied != snapshot["files"]:
            raise ValueError(
                "Disposable {} copy bytes or modes do not match tracked snapshot.".format(
                    copy_name
                )
            )
    snapshot_path = destination / "snapshot.json"
    snapshot_path.write_text(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":")), encoding="utf-8"
    )


def prepare(repository, destination):
    error = validate(repository)
    if error:
        return error
    try:
        require_clean_tracked_tree(repository)
        snapshot = tracked_snapshot(repository)
        copy_snapshot(repository, destination, snapshot)
    except (OSError, ValueError) as error:
        return str(error)
    return None


def verify_snapshot(repository, snapshot_path):
    error = validate(repository)
    if error:
        return error
    try:
        require_clean_tracked_tree(repository)
        expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
        actual = tracked_snapshot(repository)
    except (OSError, ValueError) as error:
        return str(error)
    if actual != expected:
        return "Tracked-tree snapshot changed during verification."
    return None


def main(arguments):
    if len(arguments) == 1:
        repository = Path(__file__).resolve().parent.parent
        error = validate(repository)
    elif len(arguments) == 2:
        repository = Path(arguments[1]).resolve()
        error = validate(repository)
    elif len(arguments) == 4 and arguments[1] == "prepare":
        repository = Path(arguments[2]).resolve()
        error = prepare(repository, Path(arguments[3]).resolve())
    elif len(arguments) == 4 and arguments[1] == "verify":
        repository = Path(arguments[2]).resolve()
        error = verify_snapshot(repository, Path(arguments[3]).resolve())
    elif len(arguments) >= 3 and arguments[1] == "tools":
        error = validate_trusted_tools(arguments[2:])
    else:
        print(
            "Usage: check-workflow-checkout.py [REPOSITORY_ROOT] | "
            "prepare REPOSITORY_ROOT DESTINATION | "
            "verify REPOSITORY_ROOT SNAPSHOT",
            file=sys.stderr,
        )
        return 2
    if error:
        print(error, file=sys.stderr)
        return 1

    print("Canonical GitHub Actions and Makefile contract checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
