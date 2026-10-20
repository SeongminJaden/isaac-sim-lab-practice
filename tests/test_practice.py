"""표준 라이브러리 검사. 실행기 계약 검사에만 가짜 git/uv를 쓰며 GPU 성공으로 간주하지 않는다."""
import importlib.util  # 숫자로 시작하는 예제 파일을 모듈로 읽는다.
import json  # 실행기가 전달한 인자 배열을 검사한다.
import math  # NaN·무한대 입력을 만든다.
import os  # 현재 OS와 테스트 전용 환경 변수를 다룬다.
from pathlib import Path  # 임시 폴더와 실습 파일 경로를 다룬다.
import shutil  # 현재 OS에서 실행할 셸을 찾는다.
import subprocess  # 실제 PowerShell 또는 Bash 프로세스를 실행한다.
import sys  # 이 검사를 시작한 Python으로 CPU 예제를 실행한다.
import tempfile  # 모의 도구와 정책 파일을 매번 격리한다.
import unittest  # 검사 결과를 모아 성공·실패를 판정한다.

ROOT = Path(__file__).resolve().parents[1]  # 실습자료의 루트 폴더다.
PIN = "ae37b028ea415c91ea2bc32609efcd759ed2b974"  # 강의에서 확인한 공식 EA 소스 버전이다.
WINDOWS = os.name == "nt"  # 각 OS의 네이티브 실행기만 시험한다.
SHELL = shutil.which("powershell" if WINDOWS else "bash")  # Windows에서는 PowerShell 5.1을 우선 사용한다.
spec = importlib.util.spec_from_file_location("reward_design", ROOT / "examples/03_reward_design.py")  # CPU 예제의 위치다.
reward_module = importlib.util.module_from_spec(spec)  # 임시 모듈 객체를 만든다.
spec.loader.exec_module(reward_module)  # __main__이 아니므로 CSV 출력은 실행하지 않는다.


def run(command, **kwargs):  # 모든 하위 프로세스에 동일한 출력·시간 제한을 적용한다.
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45, **kwargs)  # 멈춘 검사를 무한히 기다리지 않는다.


class CalculationTests(unittest.TestCase):  # GPU 없이 실제 계산을 검증한다.
    def test_reward_examples(self):  # 강의의 6개 보상 관계와 기본 입력 거부를 확인한다.
        reward_module.self_check()  # 접근·후퇴·정지·도착·충돌·왕복의 기대값을 검사한다.

    def test_invalid_numbers(self):  # 숫자 경계가 학습 보상으로 전파되지 않는지 확인한다.
        for values in ((math.inf, 1, 1), (1, -math.inf, 1), (1, 0, math.nan), (1, 0, -1), (1, -1, 1)):
            with self.subTest(values=values), self.assertRaises(ValueError):  # 각 입력마다 명시적 오류를 기대한다.
                reward_module.reward(*values)  # 실제 보상 함수를 호출한다.

    def test_collision_has_priority(self):  # 도착·충돌이 같은 스텝에 보고되는 경계를 확인한다.
        self.assertAlmostEqual(reward_module.reward(0.2, 0, 0.1, True, True), -19.601)  # 도착 보상을 중복 지급하지 않는다.

    def test_examples_reject_bad_options_before_sim_import(self):  # 잘못된 옵션을 GPU 초기화 전에 거부하는지 검사한다.
        cases = [("01_drop_cubes.py", "--height", "0.25"), ("01_drop_cubes.py", "--gravity", "nan"), ("01_drop_cubes.py", "--frames", "0"), ("02_camera_capture.py", "--frames", "29")]  # 유효 범위 바로 밖을 선택한다.
        for filename, flag, value in cases:  # 각 예제를 일반 Python에서 실행한다.
            with self.subTest(filename=filename, flag=flag):  # 실패 사례를 구분해 보고한다.
                result = run([sys.executable, str(ROOT / "examples" / filename), flag, value])  # Sim을 설치하지 않아도 거부되어야 한다.
                self.assertEqual(result.returncode, 2, result.stderr)  # argparse의 입력 오류 종료 코드다.
                self.assertNotIn("ModuleNotFoundError", result.stderr)  # Sim import까지 내려가면 검사 실패다.

    def test_example_help_without_gpu(self):  # 설치 전에도 예제 사용법을 볼 수 있어야 한다.
        for filename in ("01_drop_cubes.py", "02_camera_capture.py"):  # GPU 예제 두 개를 확인한다.
            result = run([sys.executable, str(ROOT / "examples" / filename), "--help"])  # argparse의 도움말 경로다.
            self.assertEqual(result.returncode, 0, result.stderr)  # Sim import 없이 정상 종료해야 한다.


@unittest.skipUnless(SHELL, "Native shell is required")  # 셸이 없는 환경에서는 실행기 검사를 건너뛰었다고 명시한다.
class LauncherTests(unittest.TestCase):  # 실제 셸에서 옵션 전달과 실패 처리 계약을 확인한다.
    def preview(self, mode, extra=()):  # 설치나 GPU 실행 없이 인자를 관찰한다.
        if WINDOWS:  # Windows용 PowerShell 매개변수 형식이다.
            command = [SHELL, "-NoProfile", "-NonInteractive", "-File", str(ROOT / "04_cartpole.ps1"), "-Mode", mode, "-PrintCommand", *extra]
        else:  # Ubuntu용 GNU 옵션 형식이다.
            command = [SHELL, str(ROOT / "ubuntu/04_cartpole.sh"), "--mode", mode.lower(), "--print-command", *extra]
        return run(command)  # 결과를 호출자가 검사한다.

    def options(self, windows, ubuntu):  # 이 OS에 해당하는 옵션 목록을 고른다.
        return windows if WINDOWS else ubuntu  # 다른 OS의 인자를 섞지 않는다.

    def test_all_modes_match_upstream_cli(self):  # Sim 6.1 EA의 공식 명령 이름을 회귀 검사한다.
        expected = {"Setup": "sync", "List": "scripts/environments/list_envs.py", "Random": "random_agent", "Train": "train", "Play": "play"}  # List는 CLI 하위 명령이 아닌 실제 스크립트다.
        for mode, action in expected.items():  # 모든 사용자 진입점을 검사한다.
            with self.subTest(mode=mode):  # 실패한 단계를 구분한다.
                result = self.preview(mode)  # 실제 배포 스크립트로 인자를 만든다.
                self.assertEqual(result.returncode, 0, result.stderr)  # 미리보기는 환경 설치 없이 성공해야 한다.
                data = json.loads(result.stdout)  # 문자열 경계까지 확인한다.
                self.assertEqual(data["commit"], PIN)  # 문서와 실행기가 같은 버전을 사용한다.
                self.assertIn(action, data["arguments"])  # 공식 하위 명령이 들어 있어야 한다.
                self.assertIn("--frozen", data["arguments"])  # 의존성을 임의 갱신하지 않는다.
                if mode == "List":  # 고정 EA 소스의 목록 스크립트 호출을 확인한다.
                    self.assertEqual(data["arguments"], ["run", "--frozen", "--extra", "isaacsim", "python", "scripts/environments/list_envs.py", "--show_presets"])  # 지원하지 않는 isaaclab list_envs 호출을 막는다.
                if mode in ("Random", "Train", "Play"):  # 물리 실행이 있는 단계다.
                    self.assertIn("Isaac-Cartpole", data["arguments"])  # 수업 과제 이름을 확인한다.
                    self.assertIn("physics=isaacsim_physx", data["arguments"])  # PhysX 선택이 누락되면 실패한다.

    def test_training_overrides(self):  # 낮은 환경 수·짧은 학습·창 없는 실행을 선택할 수 있어야 한다.
        extra = self.options(["-NumEnvs", "2", "-Iterations", "3", "-Viz", "none"], ["--num-envs", "2", "--iterations", "3", "--viz", "none"])  # 양쪽에서 같은 설정이다.
        result = self.preview("Train", extra)  # 설정을 실제 실행기에 전달한다.
        self.assertEqual(result.returncode, 0, result.stderr)  # 정상 옵션이어야 한다.
        args = json.loads(result.stdout)["arguments"]  # CLI 배열을 읽는다.
        for key, expected in (("--num_envs", "2"), ("--max_iterations", "3"), ("--viz", "none"), ("--seed", "42")):
            self.assertEqual(args[args.index(key) + 1], expected)  # 값이 다른 옵션에 붙지 않았는지 검사한다.

    def test_checkpoint_spaces_stay_one_argument(self):  # 공백 포함 경로를 셸이 분할하지 않아야 한다.
        filename = "saved policies/model 3.pt"  # 공백을 두 군데 포함한다.
        extra = self.options(["-Checkpoint", filename], ["--checkpoint", filename])  # OS별 옵션 이름이다.
        data = json.loads(self.preview("Play", extra).stdout)  # 미리보기에서는 실제 파일이 필요 없다.
        args = data["arguments"]  # 토큰 배열을 확인한다.
        self.assertEqual(args[args.index("--checkpoint") + 1], filename)  # 단일 토큰으로 유지해야 한다.

    def test_invalid_values_fail(self):  # 오타와 범위 오류가 실행으로 이어지지 않아야 한다.
        cases = [("-NumEnvs", "--num-envs", "0"), ("-NumEnvs", "--num-envs", "4097"), ("-Iterations", "--iterations", "0"), ("-Viz", "--viz", "typo")]
        for win, linux, value in cases:  # 각 경계를 독립적으로 검사한다.
            result = self.preview("Train", self.options([win, value], [linux, value]))  # 실제 파서를 사용한다.
            self.assertNotEqual(result.returncode, 0, result.stdout)  # 실패를 성공으로 보고하면 안 된다.

    def test_shell_syntax(self):  # 배포한 이 OS의 모든 셸 파일을 구문 분석한다.
        if WINDOWS:  # PowerShell 파서는 실행 없이 오류 목록을 반환한다.
            command = "$errorsFound=0; Get-ChildItem -LiteralPath $env:COURSE_ROOT -Filter *.ps1 | ForEach-Object { $t=$null; $e=$null; [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$t,[ref]$e); if($e){$e; $errorsFound++} }; exit $errorsFound"  # 관리자 권한이나 정책 변경을 하지 않는다.
            result = run([SHELL, "-NoProfile", "-NonInteractive", "-Command", command], env={**os.environ, "COURSE_ROOT": str(ROOT)})  # 경로는 환경 변수로 안전하게 전달한다.
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)  # 문법 오류가 없어야 한다.
        else:  # Bash의 -n은 명령을 실행하지 않는다.
            for path in (ROOT / "ubuntu").glob("*.sh"):  # 설치·진단·실행 스크립트를 모두 검사한다.
                result = run([SHELL, "-n", str(path)])  # 설치 작업은 수행하지 않는다.
                self.assertEqual(result.returncode, 0, result.stderr)  # 문법 오류를 보고한다.

    def guarded_run(self, *, head=PIN, dirty="", checkpoint="latest", exit_code=0, mode="Play", make_file=False):  # 외부 도구만 모의 구현하여 실행기 분기를 시험한다.
        with tempfile.TemporaryDirectory(prefix="isaac course ") as temporary:  # 공백 있는 경로를 매번 새로 만든다.
            base = Path(temporary)  # 테스트 외부 파일을 건드리지 않는다.
            lab = base / "lab checkout"  # 작업 폴더 전환을 관찰할 경로다.
            (lab / ".git").mkdir(parents=True)  # git 모의 도구가 검사할 가짜 checkout 표시다.
            capture = base / "called.json"  # uv에 도달했는지 확인할 증거 파일이다.
            after = base / "after.txt"  # PowerShell의 원래 위치 복원 여부를 확인한다.
            if make_file:  # 경로 전달 검사에서만 더미 파일을 만든다.
                (base / checkpoint).parent.mkdir(parents=True, exist_ok=True)  # 정책 폴더를 만든다.
                (base / checkpoint).write_text("TEST ONLY: not a trained policy", encoding="utf-8")  # 실제 모델로 오인하지 않게 표시한다.
            env = {**os.environ, "TEST_HEAD": head, "TEST_DIRTY": dirty, "TEST_CAPTURE": str(capture), "TEST_EXIT": str(exit_code), "TEST_LAB": str(lab), "TEST_MODE": mode, "TEST_CHECKPOINT": checkpoint, "TEST_AFTER": str(after)}  # 이 자식 프로세스에만 전달한다.
            if WINDOWS:  # PowerShell 함수가 이 테스트 프로세스 안에서만 git/uv를 대체한다.
                env["TEST_SCRIPT"] = str(ROOT / "04_cartpole.ps1")  # 실행할 실제 배포 스크립트다.
                harness = """
# 테스트 전용 Git 응답이다. 실제 저장소를 변경하지 않는다.
function git { if ($args -contains 'rev-parse') { $env:TEST_HEAD }; if ($args -contains 'status' -and $env:TEST_DIRTY) { $env:TEST_DIRTY }; $global:LASTEXITCODE=0 }
# 실제 학습 대신 인자와 작업 폴더를 기록하고 지정한 종료 코드를 전달한다.
function uv { @{cwd=(Get-Location).Path;arguments=@($args)} | ConvertTo-Json -Compress | Set-Content -LiteralPath $env:TEST_CAPTURE -Encoding UTF8; $global:LASTEXITCODE=[int]$env:TEST_EXIT }
# 실제 배포 스크립트의 성공·실패 흐름을 그대로 실행한다.
try { & $env:TEST_SCRIPT -Mode $env:TEST_MODE -LabDir $env:TEST_LAB -Checkpoint $env:TEST_CHECKPOINT }
# 예외를 테스트 프로세스의 실패로 전달한다.
catch { Write-Output $_; exit 1 }
# 실패해도 원래 폴더가 복원됐는지 기록한다.
finally { (Get-Location).Path | Set-Content -LiteralPath $env:TEST_AFTER -Encoding UTF8 }
"""  # 함수 모의 구현은 이 호출이 끝나면 사라진다.
                result = run([SHELL, "-NoProfile", "-NonInteractive", "-Command", harness], cwd=base, env=env)  # 실제 PowerShell에서 실행한다.
                self.assertEqual(Path(after.read_text(encoding="utf-8-sig").strip()), base)  # 성공·예외 모두 위치를 복원해야 한다.
            else:  # Bash는 이 테스트의 PATH 앞에 둔 모의 실행 파일을 사용한다.
                binary = base / "bin"  # 시스템 도구를 수정하지 않는 임시 경로다.
                binary.mkdir()  # 모의 도구 폴더를 만든다.
                (binary / "git").write_text('#!/usr/bin/env bash\n# 테스트 전용 커밋·상태 응답이다.\ncase "$*" in *rev-parse*) printf "%s\\n" "$TEST_HEAD" ;; *status*) printf "%s" "$TEST_DIRTY" ;; esac\n', encoding="utf-8")  # 필요한 읽기 동작만 흉내 낸다.
                (binary / "uv").write_text('#!/usr/bin/env python3.12\nimport json, os, sys  # 모의 실행 기록에 필요한 표준 모듈이다.\nwith open(os.environ["TEST_CAPTURE"], "w", encoding="utf-8") as stream:  # 인자와 작업 위치를 기록한다.\n    json.dump({"cwd": os.getcwd(), "arguments": sys.argv[1:]}, stream)  # 학습은 실행하지 않는다.\nsys.exit(int(os.environ["TEST_EXIT"]))  # 지정한 실패 코드를 전파한다.\n', encoding="utf-8")  # 실제 uv와 무관한 모의 실행기다.
                for tool in binary.iterdir():  # 생성한 두 파일만 실행 가능하게 한다.
                    tool.chmod(0o755)  # 시스템 파일의 권한은 변경하지 않는다.
                env["PATH"] = str(binary) + os.pathsep + env["PATH"]  # 이 자식 프로세스에만 적용한다.
                result = run([SHELL, str(ROOT / "ubuntu/04_cartpole.sh"), "--mode", mode.lower(), "--lab-dir", str(lab), "--checkpoint", checkpoint], cwd=base, env=env)  # 실제 Bash 실행기를 호출한다.
            data = json.loads(capture.read_text(encoding="utf-8-sig")) if capture.exists() else None  # uv에 도달하지 않았다면 None이다.
            return result, data, str((base / checkpoint).resolve()), str(lab)  # 임시 폴더 제거 전에 결과만 반환한다.

    def test_wrong_checkout_stops_before_uv(self):  # 다른 버전의 Lab에 의존성을 덮어 설치하면 안 된다.
        result, data, _, _ = self.guarded_run(head="0" * 40)  # 잘못된 커밋을 응답시킨다.
        self.assertNotEqual(result.returncode, 0)  # 버전 불일치는 실패다.
        self.assertIsNone(data)  # uv는 호출되지 않아야 한다.

    def test_modified_checkout_stops_before_uv(self):  # 사용자가 바꾼 소스를 자동으로 되돌리거나 실행하지 않는다.
        result, data, _, _ = self.guarded_run(dirty=" M pyproject.toml")  # 추적 파일 변경을 응답시킨다.
        self.assertNotEqual(result.returncode, 0)  # 변경된 checkout은 별도 확인이 필요하다.
        self.assertIsNone(data)  # 의존성 설치나 학습을 시작하지 않는다.

    def test_missing_checkpoint_stops_before_uv(self):  # 없는 모델을 최신 모델로 조용히 바꾸면 안 된다.
        result, data, _, _ = self.guarded_run(checkpoint="missing.pt")  # 존재하지 않는 파일이다.
        self.assertNotEqual(result.returncode, 0)  # 명시적인 오류여야 한다.
        self.assertIsNone(data)  # GPU 초기화 전에 실패해야 한다.

    def test_relative_checkpoint_resolved_before_cd(self):  # Lab 폴더로 이동한 뒤 상대 경로가 깨지는 회귀를 막는다.
        result, data, expected, lab = self.guarded_run(checkpoint="saved policies/model 3.pt", make_file=True)  # 원래 폴더 기준의 공백 경로다.
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)  # 가짜 uv는 성공하도록 설정했다.
        self.assertEqual(data["cwd"], lab)  # uv는 Lab 프로젝트 폴더에서 실행되어야 한다.
        args = data["arguments"]  # 실제 전달된 인자를 읽는다.
        self.assertEqual(args[args.index("--checkpoint") + 1], expected)  # 경로는 하나의 절대 경로 인자여야 한다.

    def test_uv_failure_is_not_reported_as_success(self):  # 외부 학습 프로세스 실패를 호출자가 알 수 있어야 한다.
        result, data, _, _ = self.guarded_run(mode="Train", exit_code=7)  # 가짜 학습이 실패하게 한다.
        self.assertIsNotNone(data)  # uv 호출까지 진행한 시험임을 확인한다.
        self.assertNotEqual(result.returncode, 0)  # 실패를 종료 코드에 반영해야 한다.

    def test_setup_existing_pin_uses_frozen_sync(self):  # 이미 준비한 올바른 checkout에서는 잠금 설치만 수행한다.
        result, data, _, lab = self.guarded_run(mode="Setup")  # 네트워크 clone은 모의하지 않는다.
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)  # 설치 인자 전달이 성공해야 한다.
        self.assertEqual(data["cwd"], lab)  # 올바른 프로젝트에서 설치한다.
        self.assertEqual(data["arguments"], ["sync", "--frozen", "--extra", "isaacsim"])  # 임의 업그레이드가 없어야 한다.


if __name__ == "__main__":  # 이 파일을 직접 실행해도 동일한 검사를 수행한다.
    unittest.main()  # 결과와 종료 코드를 unittest가 관리한다.
