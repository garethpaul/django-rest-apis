#!/usr/bin/env python3
import _hashlib
import os
import stat
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "scripts" / "check-workflow-checkout.py"
CANONICAL_WORKFLOW = ROOT / ".github" / "workflows" / "check.yml"
CANONICAL_MAKEFILE = ROOT / "Makefile"
TRUSTED_GIT_FIXTURE = ROOT / "scripts" / "trusted-git-fixture.sh"
CANONICAL_WORKFLOW_SHA256 = (
    "f5cdeb4df78224823a02eeade8a74f75dc0110b0dc0b6e75d6577fa09400a2e2"
)
CANONICAL_MAKEFILE_SHA256 = (
    "44a135e49ca4c3b7f5c9d3e05c449fa63f66ce6d29c1122ed5f46b1b1c15a862"
)
SANITIZED_PYTHON = (
    "/usr/bin/env",
    "-u",
    "PYTHONPATH",
    "-u",
    "PYTHONHOME",
    "PYTHONNOUSERSITE=1",
    "PYTHONDONTWRITEBYTECODE=1",
    sys.executable,
    "-I",
    "-S",
)
SANITIZED_ENVIRONMENT_VARIABLES = (
    "PYTHONPATH",
    "PYTHONHOME",
    "MAKEFILES",
    "MAKEFLAGS",
    "MFLAGS",
    "GNUMAKEFLAGS",
)


def sanitized_environment(overrides=None):
    environment = os.environ.copy()
    for variable in SANITIZED_ENVIRONMENT_VARIABLES:
        environment.pop(variable, None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    if overrides:
        environment.update(overrides)
    return environment


REVIEW_BYPASSES = {
    "escaped-key": '- "\\u0075ses": actions/checkout@v6\n',
    "explicit-key": "- ? uses\n  : actions/checkout@v6\n",
    "tagged-key": "- !!str uses: actions/checkout@v6\n",
    "tagged-value": "- uses: !!str actions/checkout@v6\n",
    "nested-plain-scalar": "- uses:\n    actions/checkout@v6\n",
}


class CanonicalActionsContractTests(unittest.TestCase):
    def create_repository(self):
        temporary_directory = tempfile.TemporaryDirectory()
        repository = Path(temporary_directory.name)
        workflow = repository / ".github" / "workflows" / "check.yml"
        workflow.parent.mkdir(parents=True)
        shutil.copyfile(CANONICAL_WORKFLOW, workflow)
        shutil.copyfile(CANONICAL_MAKEFILE, repository / "Makefile")
        return temporary_directory, repository

    def run_checker(
        self, repository, expected_returncode, checker=CHECKER, environment=None
    ):
        result = subprocess.run(
            [*SANITIZED_PYTHON, str(checker), str(repository)],
            check=False,
            capture_output=True,
            text=True,
            env=sanitized_environment(environment),
        )
        self.assertEqual(
            expected_returncode,
            result.returncode,
            "stdout:\n{}\nstderr:\n{}".format(result.stdout, result.stderr),
        )
        return result

    def assert_rejected(self, mutate, message):
        temporary_directory, repository = self.create_repository()
        with temporary_directory:
            mutate(repository)
            result = self.run_checker(repository, 1)
        self.assertIn(message, result.stderr)

    def test_repository_contract_passes(self):
        result = self.run_checker(ROOT, 0)
        self.assertIn(
            "Canonical GitHub Actions and Makefile contract checks passed",
            result.stdout,
        )

    def test_canonical_workflow_and_makefile_bytes_are_exact(self):
        contracts = (
            (CANONICAL_WORKFLOW, CANONICAL_WORKFLOW_SHA256),
            (CANONICAL_MAKEFILE, CANONICAL_MAKEFILE_SHA256),
        )
        for path, expected_digest in contracts:
            with self.subTest(path=path):
                digest = _hashlib.openssl_sha256(path.read_bytes()).hexdigest()
                self.assertEqual(expected_digest, digest)

    def test_workflow_runs_checker_before_make(self):
        workflow = CANONICAL_WORKFLOW.read_text(encoding="utf-8")
        required_fragments = (
            '"$python_path" -I -S scripts/check-workflow-checkout.py tools',
            '"$python_path" -I -S scripts/check-workflow-checkout.py prepare',
            '/usr/bin/mkdir -p "$contract_dir/build"',
            '> "$contract_dir/build/Dockerfile"',
            '"$docker_path" build',
        )
        positions = []
        for fragment in required_fragments:
            self.assertEqual(1, workflow.count(fragment), fragment)
            positions.append(workflow.index(fragment))
        self.assertEqual(sorted(positions), positions)
        self.assertGreaterEqual(workflow.count('"$docker_path" run'), 4)
        self.assertIn("--read-only", workflow)
        self.assertIn("--network none", workflow)
        self.assertIn("--cap-drop ALL", workflow)
        self.assertIn("--security-opt no-new-privileges", workflow)
        self.assertIn("--user 65534:65534", workflow)
        self.assertIn('"$contract_dir/tests/repository:/workspace:ro"', workflow)
        self.assertIn('"$contract_dir/verifier/repository:/verifier:ro"', workflow)
        test_block = workflow.split("Run copied contract tests", 1)[1].split(
            "Verify source before Make", 1
        )[0]
        self.assertNotIn("$GITHUB_WORKSPACE:/source", test_block)
        self.assertNotIn("/verifier", test_block)
        self.assertIn("PATH=/usr/bin:/bin", workflow)
        self.assertIn("/usr/bin/realpath", workflow)
        self.assertIn("PYTHONNOUSERSITE=1", workflow)
        self.assertIn("-u GNUMAKEFLAGS", workflow)
        self.assertIn("/usr/bin/make", workflow)
        self.assertIn("-f /workspace/Makefile", workflow)

    def test_rejects_added_workflow(self):
        def mutate(repository):
            shutil.copyfile(
                repository / ".github" / "workflows" / "check.yml",
                repository / ".github" / "workflows" / "extra.yml",
            )

        self.assert_rejected(mutate, "workflow inventory")

    def test_rejects_duplicate_workflow_file(self):
        def mutate(repository):
            duplicate = repository / ".github" / "workflows" / "duplicate.yaml"
            duplicate.write_bytes(CANONICAL_WORKFLOW.read_bytes())

        self.assert_rejected(mutate, "workflow inventory")

    def test_rejects_any_workflow_content_mutation(self):
        def mutate(repository):
            workflow = repository / ".github" / "workflows" / "check.yml"
            workflow.write_bytes(workflow.read_bytes() + b"# mutation\n")

        self.assert_rejected(mutate, "SHA-256 mismatch")

    def test_rejects_line_ending_change(self):
        def mutate(repository):
            workflow = repository / ".github" / "workflows" / "check.yml"
            workflow.write_bytes(workflow.read_bytes().replace(b"\n", b"\r\n"))

        self.assert_rejected(mutate, "SHA-256 mismatch")

    def test_rejects_workflow_command_noop_bypass(self):
        def mutate(repository):
            workflow = repository / ".github" / "workflows" / "check.yml"
            content = workflow.read_text(encoding="utf-8")
            workflow.write_text(
                content.replace(
                    "            /usr/bin/make -C /workspace -f /workspace/Makefile check\n",
                    "            /usr/bin/true\n",
                ),
                encoding="utf-8",
            )

        self.assert_rejected(mutate, "SHA-256 mismatch")

    def test_rejects_added_local_composite_action(self):
        def mutate(repository):
            action = repository / ".github" / "actions" / "hidden-checkout" / "action.yml"
            action.parent.mkdir(parents=True)
            action.write_text(
                textwrap.dedent(
                    """\
                    name: hidden checkout
                    description: restores checkout credentials
                    runs:
                      using: composite
                      steps:
                        - uses: actions/checkout@v6
                        - shell: bash
                          run: echo done
                    """
                ),
                encoding="utf-8",
            )

        self.assert_rejected(mutate, "local action inventory")

    def test_rejects_added_local_action_yaml(self):
        def mutate(repository):
            action = repository / ".github" / "actions" / "example" / "action.yaml"
            action.parent.mkdir(parents=True)
            action.write_text("name: example\nruns:\n  using: composite\n  steps: []\n", encoding="utf-8")

        self.assert_rejected(mutate, "local action inventory")

    def test_rejects_unreviewed_empty_local_actions_root(self):
        def mutate(repository):
            (repository / ".github" / "actions").mkdir(parents=True)

        self.assert_rejected(mutate, "local action inventory")

    def test_rejects_symlinked_canonical_workflow(self):
        def mutate(repository):
            workflow = repository / ".github" / "workflows" / "check.yml"
            target = repository / "workflow-target.yml"
            target.write_bytes(workflow.read_bytes())
            workflow.unlink()
            workflow.symlink_to(target)

        self.assert_rejected(mutate, "symlink")

    def test_rejects_nested_symlink_directories_without_following_them(self):
        for surface in ("workflows", "actions"):
            with self.subTest(surface=surface):
                def mutate(repository, surface=surface):
                    target = repository / "real-action"
                    target.mkdir()
                    (target / "action.yml").write_text(
                        "name: linked\nruns:\n  using: composite\n  steps: []\n",
                        encoding="utf-8",
                    )
                    nested = repository / ".github" / surface / "nested"
                    nested.parent.mkdir(parents=True, exist_ok=True)
                    nested.symlink_to(target, target_is_directory=True)

                self.assert_rejected(mutate, "symlink")

    def test_rejects_adjacent_symlinks_and_non_regular_entries(self):
        cases = (
            ("workflows-file-symlink", "workflows", "symlink"),
            ("actions-file-symlink", "actions", "symlink"),
            ("workflows-fifo", "workflows", "non-regular"),
            ("actions-fifo", "actions", "non-regular"),
            ("workflows-empty-directory", "workflows", "inventory"),
            ("actions-empty-directory", "actions", "inventory"),
        )
        for name, surface, expected_message in cases:
            with self.subTest(name=name):
                def mutate(repository, name=name, surface=surface):
                    entry = repository / ".github" / surface / "adjacent"
                    entry.parent.mkdir(parents=True, exist_ok=True)
                    if name.endswith("file-symlink"):
                        target = repository / "target.txt"
                        target.write_text("target\n", encoding="utf-8")
                        entry.symlink_to(target)
                    elif name.endswith("fifo"):
                        os.mkfifo(entry)
                    else:
                        entry.mkdir()

                self.assert_rejected(mutate, expected_message)

    def test_rejects_every_review_yaml_bypass(self):
        for name, bypass in REVIEW_BYPASSES.items():
            with self.subTest(name=name):
                def mutate(repository, bypass=bypass):
                    workflow = repository / ".github" / "workflows" / "check.yml"
                    workflow.write_text(
                        workflow.read_text(encoding="utf-8") + bypass,
                        encoding="utf-8",
                    )

                self.assert_rejected(mutate, "SHA-256 mismatch")

    def test_make_check_dry_run_reaches_every_gate(self):
        result = subprocess.run(
            ["make", "-n", "-C", str(ROOT), "check"],
            check=True,
            capture_output=True,
            text=True,
        )
        expected_commands = (
            "scripts/check-baseline.sh",
            "scripts/test-settings-helpers.py",
            "scripts/test-view-helpers.py",
            "scripts/test-workflow-checkout.py",
            " -m py_compile ",
            "scripts/check-workflow-checkout.py",
        )
        for expected_command in expected_commands:
            self.assertIn(expected_command, result.stdout)

    def test_rejects_makefile_noop_and_python_override_mutations(self):
        mutations = {
            "noop": ".PHONY: check\ncheck:\n\t@true\n",
            "python-overridable": CANONICAL_MAKEFILE.read_text(
                encoding="utf-8"
            ).replace(
                "override PYTHON := env -u PYTHONPATH -u PYTHONHOME "
                "-u MAKEFILES -u MAKEFLAGS -u MFLAGS -u GNUMAKEFLAGS "
                "PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 python3 -I -S "
                "-X pycache_prefix=$${TMPDIR:-/tmp}/django-rest-apis-pycache-$$$$",
                "PYTHON ?= python3",
            ),
            "line-endings": CANONICAL_MAKEFILE.read_bytes().replace(
                b"\n", b"\r\n"
            ),
        }
        for name, content in mutations.items():
            with self.subTest(name=name):
                def mutate(repository, content=content):
                    if isinstance(content, bytes):
                        (repository / "Makefile").write_bytes(content)
                    else:
                        (repository / "Makefile").write_text(content, encoding="utf-8")

                self.assert_rejected(mutate, "Makefile SHA-256 mismatch")

    def test_rejects_makefile_symlink_and_non_regular_types(self):
        for kind in ("symlink", "fifo"):
            with self.subTest(kind=kind):
                def mutate(repository, kind=kind):
                    makefile = repository / "Makefile"
                    makefile.unlink()
                    if kind == "symlink":
                        target = repository / "Makefile.target"
                        target.write_bytes(CANONICAL_MAKEFILE.read_bytes())
                        makefile.symlink_to(target)
                    else:
                        os.mkfifo(makefile)

                self.assert_rejected(mutate, "Canonical repository file must be regular")

    def test_rejects_combined_unsafe_workflow_and_noop_makefile(self):
        def mutate(repository):
            workflow = repository / ".github" / "workflows" / "check.yml"
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "persist-credentials: false", "persist-credentials: true"
                ),
                encoding="utf-8",
            )
            (repository / "Makefile").write_text(
                ".PHONY: check\ncheck:\n\t@true\n", encoding="utf-8"
            )

        self.assert_rejected(mutate, "SHA-256 mismatch")

    def test_python_override_cannot_replace_test_interpreter(self):
        invocations = (
            (["make", "-n", "-C", str(ROOT), "PYTHON=true", "check"], None),
            (["make", "-n", "-C", str(ROOT), "check"], {"PYTHON": "true"}),
        )
        for command, environment_override in invocations:
            with self.subTest(command=command, environment=environment_override):
                environment = sanitized_environment(environment_override)
                result = subprocess.run(
                    command,
                    check=True,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                self.assertIn("python3 ", result.stdout)
                self.assertNotIn("true ", result.stdout)

    def test_isolated_checker_ignores_pythonpath_sitecustomize_and_shadowing(self):
        temporary_directory, repository = self.create_repository()
        with temporary_directory, tempfile.TemporaryDirectory() as hook_directory:
            workflow = repository / ".github" / "workflows" / "check.yml"
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "persist-credentials: false", "persist-credentials: true"
                ),
                encoding="utf-8",
            )
            Path(hook_directory, "sitecustomize.py").write_text(
                "import _hashlib\n_hashlib.openssl_sha256 = lambda *args, **kwargs: "
                "type('Fake', (), {'update': lambda self, value: None, "
                "'hexdigest': lambda self: 'f5cdeb4df78224823a02eeade8a74f75dc0110b0dc0b6e75d6577fa09400a2e2'})()\n",
                encoding="utf-8",
            )
            (repository / "scripts").mkdir()
            (repository / "scripts" / "_hashlib.py").write_text(
                "raise RuntimeError('shadowed _hashlib imported')\n", encoding="utf-8"
            )
            result = self.run_checker(
                repository,
                1,
                environment={"PYTHONPATH": hook_directory, "PYTHONNOUSERSITE": "0"},
            )
        self.assertIn("SHA-256 mismatch", result.stderr)

    def test_prepare_copy_and_verify_detect_source_mutation_after_tests(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory) / "repository"
            shutil.copytree(ROOT, repository, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "--all"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "-c",
                    "user.name=Contract Test",
                    "-c",
                    "user.email=contract@example.invalid",
                    "commit",
                    "-qm",
                    "snapshot",
                ],
                check=True,
            )
            contract_directory = Path(temporary_directory) / "contract"
            prepare = subprocess.run(
                [
                    *SANITIZED_PYTHON,
                    str(CHECKER),
                    "prepare",
                    str(repository),
                    str(contract_directory),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=sanitized_environment(
                    {"TRUSTED_GIT": str(Path("/usr/bin/git").resolve())}
                ),
            )
            self.assertEqual(0, prepare.returncode, prepare.stderr)
            copied_makefile = contract_directory / "tests" / "repository" / "Makefile"
            copied_makefile.write_text(
                ".PHONY: check\ncheck:\n\t@true\n", encoding="utf-8"
            )
            self.assertEqual(CANONICAL_MAKEFILE.read_bytes(), (repository / "Makefile").read_bytes())
            original = (repository / "Makefile").read_bytes()
            (repository / "Makefile").write_text(
                ".PHONY: check\ncheck:\n\t@true\n", encoding="utf-8"
            )
            verify = subprocess.run(
                [
                    *SANITIZED_PYTHON,
                    str(contract_directory / "verifier" / "repository" / "scripts" / "check-workflow-checkout.py"),
                    "verify",
                    str(repository),
                    str(contract_directory / "snapshot.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=sanitized_environment(
                    {"TRUSTED_GIT": str(Path("/usr/bin/git").resolve())}
                ),
            )
            self.assertNotEqual(0, verify.returncode)
            (repository / "Makefile").write_bytes(original)
            verify_restored = subprocess.run(
                [
                    *SANITIZED_PYTHON,
                    str(contract_directory / "verifier" / "repository" / "scripts" / "check-workflow-checkout.py"),
                    "verify",
                    str(repository),
                    str(contract_directory / "snapshot.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=sanitized_environment(
                    {"TRUSTED_GIT": str(Path("/usr/bin/git").resolve())}
                ),
            )
            self.assertEqual(0, verify_restored.returncode, verify_restored.stderr)

    def test_prepare_preserves_and_validates_tracked_file_modes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory) / "repository"
            shutil.copytree(
                ROOT,
                repository,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
                copy_function=shutil.copy2,
            )
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "--all"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "-c",
                    "user.name=Contract Test",
                    "-c",
                    "user.email=contract@example.invalid",
                    "commit",
                    "-qm",
                    "snapshot",
                ],
                check=True,
            )
            contract_directory = Path(temporary_directory) / "contract"
            environment = sanitized_environment(
                {"TRUSTED_GIT": str(Path("/usr/bin/git").resolve())}
            )
            prepare = subprocess.run(
                [
                    *SANITIZED_PYTHON,
                    str(CHECKER),
                    "prepare",
                    str(repository),
                    str(contract_directory),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertEqual(0, prepare.returncode, prepare.stderr)
            source_mode = stat.S_IMODE(
                os.lstat(repository / "scripts" / "check-baseline.sh").st_mode
            )
            self.assertEqual(0o755, source_mode)
            for copy_name in ("tests", "verifier"):
                copied_script = (
                    contract_directory
                    / copy_name
                    / "repository"
                    / "scripts"
                    / "check-baseline.sh"
                )
                self.assertEqual(
                    0o755, stat.S_IMODE(os.lstat(copied_script).st_mode)
                )
                for parent in (copied_script.parent, copied_script.parent.parent):
                    parent_mode = stat.S_IMODE(os.lstat(parent).st_mode)
                    self.assertEqual(0o111, parent_mode & 0o111)

    def test_prepare_rejects_non_executable_tracked_baseline(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory) / "repository"
            shutil.copytree(
                ROOT,
                repository,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
                copy_function=shutil.copy2,
            )
            baseline = repository / "scripts" / "check-baseline.sh"
            baseline.chmod(0o644)
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "--all"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "-c",
                    "user.name=Contract Test",
                    "-c",
                    "user.email=contract@example.invalid",
                    "commit",
                    "-qm",
                    "snapshot",
                ],
                check=True,
            )
            result = subprocess.run(
                [
                    *SANITIZED_PYTHON,
                    str(CHECKER),
                    "prepare",
                    str(repository),
                    str(Path(temporary_directory) / "contract"),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=sanitized_environment(
                    {"TRUSTED_GIT": str(Path("/usr/bin/git").resolve())}
                ),
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("executable mode", result.stderr)

    def test_prepare_uses_command_local_safe_directory_for_every_git_call(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            temporary_root.chmod(0o755)
            repository = temporary_root / "repository"
            shutil.copytree(
                ROOT,
                repository,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
                copy_function=shutil.copy2,
            )
            repository.chmod(0o755)
            subprocess.run(["git", "init", "-q", str(repository)], check=True)
            subprocess.run(["git", "-C", str(repository), "add", "--all"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "-c",
                    "user.name=Contract Test",
                    "-c",
                    "user.email=contract@example.invalid",
                    "commit",
                    "-qm",
                    "snapshot",
                ],
                check=True,
            )
            argument_log = temporary_root / "git-arguments.log"
            argument_log.touch()
            argument_log.chmod(0o666)
            self.assertFalse(TRUSTED_GIT_FIXTURE.is_relative_to(temporary_root))
            self.assertEqual(
                0o755, stat.S_IMODE(os.lstat(TRUSTED_GIT_FIXTURE).st_mode)
            )
            result = subprocess.run(
                [
                    *SANITIZED_PYTHON,
                    str(CHECKER),
                    "prepare",
                    str(repository),
                    str(temporary_root / "contract"),
                ],
                check=False,
                capture_output=True,
                text=True,
                env=sanitized_environment(
                    {
                        "GIT_ARGUMENT_LOG": str(argument_log),
                        "TRUSTED_GIT": str(TRUSTED_GIT_FIXTURE),
                    }
                ),
            )
            self.assertEqual(0, result.returncode, result.stderr)
            arguments = argument_log.read_text(encoding="utf-8").splitlines()
            self.assertGreaterEqual(len(arguments), 16)
            normalized_repository = repository.resolve()
            expected_prefix = [
                "-c",
                "safe.directory={}".format(normalized_repository),
                "-C",
                str(normalized_repository),
            ]
            for offset in range(0, len(arguments), 4):
                self.assertEqual(expected_prefix, arguments[offset : offset + 4])

    def test_rejects_make_shadow_files_includes_and_makefiles_environment(self):
        shadow_paths = ("GNUmakefile", "nested/GNUmakefile", "nested/makefile")
        for relative in shadow_paths:
            with self.subTest(relative=relative):
                def mutate(repository, relative=relative):
                    path = repository / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("check:\n\t@true\n", encoding="utf-8")

                self.assert_rejected(mutate, "Make shadow")

        checker_source = CHECKER.read_text(encoding="utf-8")
        self.assertIn('MAKE_SHADOW_NAMES = ("GNUmakefile", "makefile")', checker_source)

        def include_mutation(repository):
            (repository / "Makefile").write_bytes(
                CANONICAL_MAKEFILE.read_bytes() + b"include hostile.mk\n"
            )
            (repository / "hostile.mk").write_text("check:\n\t@true\n", encoding="utf-8")

        self.assert_rejected(include_mutation, "Makefile SHA-256 mismatch")

        for variable in ("MAKEFILES", "MAKEFLAGS", "MFLAGS", "GNUMAKEFLAGS"):
            with self.subTest(variable=variable):
                temporary_directory, repository = self.create_repository()
                with temporary_directory:
                    injected = repository / "injected.mk"
                    injected.write_text("check:\n\t@true\n", encoding="utf-8")
                    value = str(injected) if variable == "MAKEFILES" else "-n"
                    result = self.run_checker(
                        repository, 1, environment={variable: value}
                    )
                self.assertIn(variable, result.stderr)

    def test_rejects_fake_path_tools_and_unresolved_executables(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            fake = Path(temporary_directory) / "python3"
            fake.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake.chmod(0o755)
            result = subprocess.run(
                [*SANITIZED_PYTHON, str(CHECKER), "tools", str(fake)],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertNotIn(str(fake), result.stderr)
        self.assertIn("Trusted executable validation failed", result.stderr)

        system_python = Path(sys.executable).resolve()
        if system_python != Path(sys.executable):
            result = subprocess.run(
                [*SANITIZED_PYTHON, str(CHECKER), "tools", sys.executable],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Trusted executable validation failed", result.stderr)

    def test_candidate_timing_mutation_has_no_source_or_verifier_mount(self):
        workflow = CANONICAL_WORKFLOW.read_text(encoding="utf-8")
        test_block = workflow.split("Run copied contract tests", 1)[1].split(
            "Verify source before Make", 1
        )[0]
        self.assertIn('"$contract_dir/tests/repository:/workspace:ro"', test_block)
        self.assertNotIn("$GITHUB_WORKSPACE", test_block)
        self.assertNotIn("$contract_dir/verifier", test_block)
        self.assertIn("--read-only", test_block)
        self.assertIn("--tmpfs /tmp:rw,nosuid,nodev,noexec", test_block)

    def test_checker_hash_self_updates_still_require_test_updates(self):
        cases = (
            ("workflow", CANONICAL_WORKFLOW_SHA256, b"# changed workflow\n"),
            ("Makefile", CANONICAL_MAKEFILE_SHA256, b"# changed Makefile\n"),
        )
        for name, expected_digest, suffix in cases:
            with self.subTest(name=name):
                temporary_directory, repository = self.create_repository()
                with temporary_directory:
                    path = (
                        repository / ".github" / "workflows" / "check.yml"
                        if name == "workflow"
                        else repository / "Makefile"
                    )
                    path.write_bytes(path.read_bytes() + suffix)
                    mutated_digest = _hashlib.openssl_sha256(path.read_bytes()).hexdigest()
                    checker = repository / "self-updated-checker.py"
                    checker.write_text(
                        CHECKER.read_text(encoding="utf-8").replace(
                            expected_digest, mutated_digest
                        ),
                        encoding="utf-8",
                    )
                    self.run_checker(repository, 0, checker=checker)
                    self.assertNotEqual(expected_digest, mutated_digest)

    def test_contract_documentation_requires_reviewed_hash_updates(self):
        plan = (
            ROOT / "docs" / "plans" / "2026-06-12-checkout-credential-boundary.md"
        ).read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        required_text = "reviewed canonical contract update"
        self.assertIn(required_text, plan)
        self.assertIn(required_text, readme)
        self.assertIn(required_text, security)


if __name__ == "__main__":
    unittest.main()
