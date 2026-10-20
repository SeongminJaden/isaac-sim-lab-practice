"""현재 OS의 CPU·실행기 검사를 수행한다. GPU 시뮬레이션 성공을 판정하지 않는다."""
from pathlib import Path  # 이 파일을 기준으로 검사할 경로를 찾는다.
import sys  # 실패 여부를 프로세스 종료 코드로 전달한다.
import unittest  # 외부 패키지 없이 회귀 검사를 실행한다.

root = Path(__file__).resolve().parent  # 터미널 위치가 달라도 같은 자료를 검사한다.
for path in [*root.glob("*.py"), *root.glob("examples/*.py"), *root.glob("tests/*.py")]:  # 배포한 모든 Python 코드를 확인한다.
    compile(path.read_text(encoding="utf-8-sig"), str(path), "exec")  # import 없이 문법만 검사하므로 Sim이 필요 없다.
suite = unittest.defaultTestLoader.discover(str(root / "tests"))  # 실제 계산과 실행기 동작 검사를 수집한다.
result = unittest.TextTestRunner(verbosity=2).run(suite)  # 검사별 성공·실패를 화면에 표시한다.
print("Scope: CPU calculations and this OS launcher contracts; simulated tools in guard tests.")  # 모의 도구를 쓰는 검사 범위를 밝힌다.
print("NOT PROVEN: Isaac Sim physics/RTX rendering, Isaac Lab GPU training or policy playback.")  # 이 검사로 알 수 없는 범위를 밝힌다.
sys.exit(0 if result.wasSuccessful() else 1)  # 하나라도 실패하면 자동 실행에서도 실패로 인식하게 한다.
