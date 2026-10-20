"""실습 3: 보상 식을 계산한다. PPO 학습이나 Isaac Sim 실행은 하지 않는다."""
import csv  # 상황별 계산 결과를 CSV로 저장한다.
import math  # 유한값 검사와 부동소수점 근삿값 비교를 사용한다.
from pathlib import Path  # 두 운영체제에서 같은 코드로 출력 경로를 만든다.


def reward(previous_distance, distance, dt, arrived=False, collision=False):  # 거리(m), 시간(s), 사건 여부를 입력받는다.
    if not all(math.isfinite(value) for value in (previous_distance, distance, dt)):  # NaN·무한대가 보상으로 전파되지 않게 한다.
        raise ValueError("Distances and dt must be finite")  # 계산할 수 없는 입력을 거부한다.
    if min(previous_distance, distance) < 0 or dt <= 0:  # 거리와 시간의 물리적 범위를 확인한다.
        raise ValueError("Distances must be non-negative and dt must be positive")  # 잘못된 단위·값을 알려준다.
    score = 2.0 * (previous_distance - distance) - 0.01 * dt  # 접근은 보상, 후퇴와 시간 소비는 비용이다.
    if collision:  # 도착과 충돌이 동시에 보고되면 충돌을 우선한다.
        score -= 20.0  # 충돌에 큰 벌점을 준다.
    elif arrived:  # 충돌 없이 도착한 경우만 도착 보상을 준다.
        score += 10.0  # 실제 환경에서는 이때 에피소드를 종료해야 반복 보상을 막을 수 있다.
    return score  # 정책 학습기에 전달할 한 스텝의 점수다.


def self_check():  # GPU 없이 확인할 수 있는 보상 식의 회귀 검사다.
    assert math.isclose(reward(2, 1.8, 0.1), 0.399)  # 접근 보상 0.4에서 시간 비용 0.001을 뺀다.
    assert math.isclose(reward(2, 2.2, 0.1), -0.401)  # 후퇴하면 거리 항도 음수가 된다.
    assert math.isclose(reward(1, 1, 0.1), -0.001)  # 정지해도 시간 비용이 든다.
    assert math.isclose(reward(0.2, 0, 0.1, arrived=True), 10.399)  # 도착 보상과 접근 보상을 합한다.
    assert math.isclose(reward(0.2, 0, 0.1, arrived=True, collision=True), -19.601)  # 충돌 우선순위를 확인한다.
    assert math.isclose(reward(1, 0.8, 0.1) + reward(0.8, 1, 0.1), -0.002)  # 왕복의 접근 보상은 상쇄된다.
    for bad in ((-1, 0, 0.1), (1, 0, 0), (1, float("nan"), 0.1)):  # 음수 거리, 0 시간, NaN을 시험한다.
        try:  # 잘못된 값은 ValueError가 발생해야 한다.
            reward(*bad)  # 튜플의 세 값을 위치 인자로 넘긴다.
        except ValueError:  # 예상한 거부 동작이다.
            pass  # 다음 잘못된 입력을 확인한다.
        else:  # 예외가 없다면 입력 검사에 결함이 있다.
            raise AssertionError(f"Invalid input was accepted: {bad}")


if __name__ == "__main__":  # 다른 테스트에서 import할 때는 파일을 쓰지 않는다.
    self_check()  # 예시 출력 전에 계산 식을 확인한다.
    cases = [  # 상황 이름, 이전 거리, 현재 거리, 도착, 충돌을 묶는다.
        ("approach", 2, 1.8, False, False),  # 접근만 한 상황이다.
        ("retreat", 2, 2.2, False, False),  # 뒤로 멀어진 상황이다.
        ("wait", 1, 1, False, False),  # 제자리에 머문 상황이다.
        ("arrive", 0.2, 0, True, False),  # 목표에 도착한 상황이다.
        ("collision", 1, 0.8, False, True),  # 접근했지만 충돌한 상황이다.
    ]
    out = Path(__file__).resolve().parents[1] / "outputs"  # 실행한 터미널 위치와 무관한 출력 폴더다.
    out.mkdir(exist_ok=True)  # 첫 실행이면 결과 폴더를 만든다.
    with (out / "reward_examples.csv").open("w", newline="", encoding="utf-8") as stream:  # 예제 표를 새로 쓴다.
        writer = csv.writer(stream)  # CSV 기록기를 만든다.
        writer.writerow(["case", "previous_distance_m", "distance_m", "dt_s", "reward"])  # 열과 단위를 기록한다.
        for name, previous, current, arrived, collision in cases:  # 각 사례를 독립적으로 계산한다.
            value = reward(previous, current, 0.1, arrived, collision)  # 사례마다 0.1초가 지났다고 가정한다.
            writer.writerow([name, previous, current, 0.1, value])  # 검토 가능한 원래 값을 저장한다.
            print(f"{name:10s} {value:8.3f}")  # 화면에서는 소수 셋째 자리까지 표시한다.
    print("Self-check passed. Output:", out / "reward_examples.csv")  # 실제 출력 위치를 알린다.
