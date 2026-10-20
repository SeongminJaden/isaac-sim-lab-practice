# Isaac Sim 6.1 · Isaac Lab 실습 — Windows / Ubuntu

상자 낙하, RGB·깊이 촬영, 보상 설계, Cartpole PPO 학습을 순서대로 진행하는 자료다. 공통 Python 예제와 Windows PowerShell·Ubuntu Bash 실행기를 제공하며, 코드에 한국어 설명을 붙였다.

**실습자료 전용 공개 저장소다.** [ZIP 다운로드](https://github.com/SeongminJaden/isaac-sim-lab-practice/archive/refs/heads/main.zip) 또는 아래 OS별 안내의 `git clone`으로 받을 수 있다. GitHub 로그인은 필요 없다.

**검증 상태(2026-10-20): Windows와 WSL Ubuntu 24.04에서 CPU·실행기 검사 각각 16개 통과. Windows Lab 의존성 설치는 완료했지만 앱 제어 정책(4551) 때문에 실행 단계가 차단됐다. GPU 물리·RTX 카메라·PPO 학습·정책 재생 성공은 아직 확인하지 못했다.** 자세한 환경과 통과 기준은 [VALIDATION.md](VALIDATION.md)를 참고한다.

## 먼저 선택할 안내

| 자료 | 내용 |
|---|---|
| [WINDOWS.md](WINDOWS.md) | Windows 11 설치부터 실습 실행까지 |
| [UBUNTU_24_04.md](UBUNTU_24_04.md) | Ubuntu 24.04 설치·Bash 실행, WSL 검사 범위 |
| [slides](slides/) | Windows·Ubuntu 명령을 나란히 배치한 기존 실습 PPTX·PDF, 33쪽 |
| [EXERCISES.md](EXERCISES.md) | 실험 조건과 결과를 적는 활동지 |
| [INSTRUCTOR.md](INSTRUCTOR.md) | 강사용 확인 기준과 해설 |
| [8GB_PROFILE.md](8GB_PROFILE.md) | 8 GB에서 사용하는 소형 설정과 제한 |

PPT의 `windows_lab`은 이 저장소를 수업용 경로에 받은 폴더 이름이다. 이름과 달리 **두 OS의 코드가 모두 포함**되어 있다. 각 OS 안내의 준비 단계가 PPT 경로와 맞춰 준다. ZIP을 받았다면 압축을 푼 폴더의 이름을 `windows_lab`으로 바꾸어 해당 경로에 둔다. PPT/PDF는 2026-10-19 제작본이며 최신 실행기 검증 기록은 위의 `VALIDATION.md`다.

**정오표(2026-10-20): PPT/PDF 24쪽의 `isaaclab list_envs --show_presets`는 이 고정 버전에서 지원하지 않는다.** Lab 폴더에서 `uv run --frozen --extra isaacsim python scripts/environments/list_envs.py --show_presets`를 사용한다. 최신 Windows·Ubuntu 실행기의 `List` 단계에는 이 수정이 반영되어 있다. 예전 ZIP을 받았다면 실행기 파일을 갱신한다.

## 실행 파일 대응

| 단계 | Windows | Ubuntu |
|---|---|---|
| OS·GPU 사전 점검 | `00_check_environment.ps1` | `ubuntu/00_check_environment.sh` |
| Sim 전용 환경 설치 | `01_install_sim.ps1` | `ubuntu/01_install_sim.sh` |
| 낙하·카메라 예제 실행 | `run_sim.ps1` | `ubuntu/run_sim.sh` |
| Lab 설치·목록·무작위·학습·재생 | `04_cartpole.ps1` | `ubuntu/04_cartpole.sh` |
| CPU·실행기 회귀 검사 | `py -3.12 99_self_check.py` | `python3.12 99_self_check.py` |

공통 코드 `examples/01_drop_cubes.py`, `02_camera_capture.py`, `scene_tools.py`는 Isaac Sim 환경에서 실행한다. `03_reward_design.py`는 일반 Python 3.12만으로 실행한다. `tests/test_practice.py`도 외부 Python 패키지가 필요 없다. 실행 결과는 `outputs/`, 학습 결과는 **Lab checkout 아래** `logs/`에 생긴다.

## 고정한 조합

- Isaac Sim `6.1.0.0`, Python 3.12, Windows 11 x64 / Ubuntu 24.04 x86_64.
- Isaac Lab 공식 `v3.0.0-EA` 태그, 커밋 `ae37b028ea415c91ea2bc32609efcd759ed2b974`.
- Lab은 `uv sync --frozen --extra isaacsim`으로 자체 `.venv`를 사용한다. 과제 `Isaac-Cartpole`, 물리 `isaacsim_physx`, RL 라이브러리 `rsl_rl`을 명시한다.
- Sim 단독 예제용 환경과 Lab 환경은 별개다. 단독 설치 스크립트는 Torch 2.11 CUDA 13 빌드, **Lab의 공식 lock은 Windows/Linux x86_64에서 Torch 2.11 CUDA 12.8 빌드**를 선택한다. Lab 환경을 수동 pip 명령으로 바꾸지 않는다.
- 실행기는 다른 커밋 또는 추적 파일 변경을 발견하면 중단한다. 사용자가 수정한 Lab을 되돌리지 않으며 새 수업용 경로를 지정하면 된다.

공식 최소 사양은 RAM 32 GB·VRAM 16 GB다. 수업의 8 GB 설정은 작은 장면·카메라 1개·Cartpole 1개로 부담을 줄이는 설정이며 실행을 보장하지 않는다. NVIDIA GPU를 직접 사용하는 Ubuntu PC에서 GPU 실습을 확인해야 한다. WSL에서 보상 코드와 Bash 검사가 통과한 사실은 RTX 실행 증거가 아니다.

## 공식 근거

- [Isaac Sim 6.1 설치](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_python.html)
- [Isaac Sim 6.1 요구 사항](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html)
- [Isaac Lab v3.0.0-EA 릴리스](https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0-EA)
- [고정 커밋의 의존성·플랫폼 설정](https://github.com/isaac-sim/IsaacLab/blob/ae37b028ea415c91ea2bc32609efcd759ed2b974/pyproject.toml)

Isaac Lab 원본은 실행기가 공식 저장소에서 별도로 받는다. 이 폴더에는 Lab 원본, 설치 환경, 학습된 정책, 실행 녹화 파일을 포함하지 않는다.
