# 검증 기록 — 2026-10-20

## 판정

**CPU 예제와 Windows·Ubuntu 실행기의 검사 각각 16개 통과. Isaac Lab Windows 의존성 설치 완료. GPU 실습 전체의 작동 검증은 미완료다.**

| 항목 | 실제 수행 | 결과 |
|---|---|---|
| Windows Python·PowerShell 검사 | Python 3.12.10 / Windows PowerShell 5.1 | 16 tests, OK, 종료 0 |
| Ubuntu Python·Bash 검사 | WSL Ubuntu 24.04.5 / Python 3.12.3 / Bash 5.2.21 | 16 tests, OK, 종료 0 |
| 보상 예제 출력 | Windows·WSL에서 실제 Python 실행 | CSV 생성, 0.399 / −0.401 / −0.001 / 10.399 / −19.601 |
| 예제 실행기·설치 보호 | 양쪽에서 도움말·잘못된 프레임 수·기존 설치 폴더 시험 | 도움말 성공, 잘못된 입력과 기존 폴더는 실패 코드로 거부 |
| Windows Lab 소스 | 공식 EA clone과 HEAD·추적 파일 상태 확인 | 지정 커밋 일치, 추적 소스 변경 없음 |
| Windows Lab 의존성 | `uv sync --frozen --extra isaacsim` | 종료 0, 설치 완료 |
| Windows Lab 인터프리터·list_envs | 새 `.venv`에서 Python 조회 및 실제 CLI 시도 | 앱 제어 정책 4551로 차단, 종료 1 |
| Windows 기존 Sim 환경의 Torch import | `import torch`와 CUDA 확인 시도 | DLL 로딩 단계에서 WinError 4551 |
| Ubuntu Sim/Lab 전체 설치 | 수행하지 않음 | 미검증 |
| GPU 낙하·RTX 카메라·PPO 학습·재생 | 이 배포본으로 성공 확인 못 함 | 미검증, 훈련 정책·성공 영상 없음 |

## 검사 내용과 한계

`99_self_check.py`는 Python 파일을 문법 검사하고 `tests/test_practice.py`를 실행한다. 보상 기대값·잘못된 숫자·GPU 예제의 초기 옵션 검사, 모든 실습 단계의 명령 생성, 환경 수와 화면 모드, 공백 경로, 체크포인트 경로 해석을 확인한다. 잘못된 커밋·수정된 원본·없는 모델을 거부하고 외부 실행 실패를 전파하는지 검사한다. Windows에서는 실패 뒤 작업 폴더 복원도 확인한다.

실행기 분기 검사에서는 **git/uv를 모의 도구로 대체**한다. 이 검사로 확인하는 것은 실행기의 입력 전달과 오류 처리다. GPU, Kit, PhysX, PPO를 모의 결과로 검증했다고 주장하지 않는다. 새 저장소 clone과 대용량 패키지 설치는 자동 회귀 검사에 포함하지 않는다.

## 실제 설치 환경

- Windows 11, RTX 5060 Laptop GPU, VRAM 8151 MiB, 드라이버 592.01, RAM 32 GB.
- Lab checkout `ae37b028ea415c91ea2bc32609efcd759ed2b974`, `uv 0.12.3`.
- uv가 준비한 CPython 3.12.13, Isaac Sim `6.1.0.0`, Torch `2.11.0+cu128`, RSL-RL `5.4.1`.
- 위 패키지 버전은 설치 완료 출력 및 배포 메타데이터 읽기로 확인했다. 차단된 Python에서 import 성공으로 확인한 값이 아니다.
- 새 Lab의 `uv pip check --python .venv/Scripts/python.exe`도 인터프리터 조회에서 차단되어 의존성 검사 통과로 기록하지 않았다.
- 장비의 드라이버 592.01은 현재 6.1 문서에 기재된 테스트 버전 595.97과 다르다. 이 차이가 4551의 원인이라고 단정하지 않는다. 8 GB VRAM도 공식 최소 16 GB 미만이다.

실제 `list_envs` 명령의 최초 오류:

```text
error: Failed to query Python interpreter at .../.venv/Scripts/python.exe
Caused by: 애플리케이션 제어 정책에서 이 파일을 차단했습니다. (os error 4551)
```

기존 Sim 환경의 `import torch`는 `shm.dll` 또는 그 의존성 로딩 단계에서 `WinError 4551`을 냈다. 이번 작업은 실행 정책 변경·보안 기능 해제·차단 파일 우회를 수행하지 않았다.

## 지원 PC에서 남은 확인

1. 각 OS 안내의 환경 점검과 Sim 호환성 검사·기본 창 실행을 완료한다.
2. 예제 01에서 실제 높이 샘플과 비어 있지 않은 CSV를 확인한다.
3. 예제 02에서 320×240 RGB와 원본 깊이, 장면 조건 파일을 확인한다.
4. Lab List와 Random을 실행하고 Cartpole 1개가 갱신되는지 확인한다.
5. Train을 2회 갱신으로 먼저 실행한다. 실제 종료·로그·체크포인트 저장을 확인한 후 300회 설정을 시험한다.
6. 생성된 실제 체크포인트를 명시하여 Play를 실행한다. 학습·재생 조건과 결과를 활동지에 기록한다.

이 항목을 완료하기 전에는 수업 장비에서 전체 실습이 검증되었다고 표시하지 않는다. 8 GB 설정의 성능·수렴 여부도 실제 결과로 판단한다.

## 소스 대조

2026-10-20에 [Sim 6.1 설치](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/install_python.html), [시스템 요구 사항](https://docs.isaacsim.omniverse.nvidia.com/6.1.0/installation/requirements.html), [Lab EA 릴리스](https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0-EA)를 확인했다. Lab의 고정 소스에서 `Isaac-Cartpole` 등록, train/play의 `rsl_rl`·체크포인트 인자, `isaacsim_physx` 선택을 대조했다. 카메라와 물리 콜백은 설치된 Sim 6.1의 API 소스와 비교했다. 소스 대조는 런타임 시험의 대체물이 아니다.
