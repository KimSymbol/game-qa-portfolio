# 역할: 캐릭터 이동 관련 테스트 케이스 (FR-004)

import allure          # Allure 리포트 데코레이터
import sys
sys.path.insert(0, ".")  # 프로젝트 루트를 모듈 탐색 경로에 추가
from utils.screen_utils import attach_screenshot


@allure.epic("Flare RPG QA")
@allure.feature("캐릭터 이동")
class TestMovement:
    def test_FR004_캐릭터_이동(self, game_playing):
        """
        FR-004: 방향키 입력 시 캐릭터가 정상적으로 이동하는지 확인

        전제조건: 플레이 가능 상태 (대화 종료)
        테스트 단계: 아래 방향 이동 키(S) 입력
        기대 결과: 미니맵의 캐릭터 위치 변화로 이동 감지
        """
        attach_screenshot("이동_전_화면")
        # 아래쪽으로 1초간 이동
        result = game_playing.move_character("down", duration=1.0)
        attach_screenshot("이동_후_화면")
        assert result, "캐릭터가 이동하지 않았습니다"