// 역할: 플레이어 체력 및 상태 효과 검증 (UT-009 ~ UT-011)

using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.UI;


public class PlayerStatusTest
{
    // ── 1. 변수 선언부 ──────────────────────────────────

    private const string BattleSceneName = "BattleScene";

    // 씬 로드 후 Player.Start() 완료까지 대기 시간
    private const float SceneReadyDelay = 1.0f;

    // 최대 체력 (Player._maxHitPoints 기본값)
    private const int MaxHitPoints = 100;

    // 체력바는 0.0~1.0 비율이므로 데미지를 비율로 환산해 비교
    private const int TestDamage = 30;
    private const int HeavyDamage = 50;
    private const int LargeHeal = 100;

    // 데미지 저항 50% 적용 시 실제 피해량은 절반
    private const float DamageResistRate = 0.5f;

    private const float Tolerance = 0.001f;

    private Player _player;
    private Slider _healthSlider;


    // ── 2. 함수 선언부 ──────────────────────────────────

    /// <summary>BattleScene 로드 후 Player 와 체력바 슬라이더를 확보한다.</summary>
    private IEnumerator LoadBattleScene()
    {
        // batchmode(CI) 환경에는 입력 장치가 없어 OnScreenControl 이 예외를 던진다.
        // 테스트 대상 로직과 무관한 환경 제약이므로 무시한다.
        LogAssert.ignoreFailingMessages = true;

        yield return SceneManager.LoadSceneAsync(BattleSceneName);
        yield return new WaitForSeconds(SceneReadyDelay);

        _player = Object.FindFirstObjectByType<Player>();
        Assert.IsNotNull(_player, "전제조건: Player 가 씬에 존재해야 함");

        // HealthBar 의 내부 필드는 private 이므로
        // 동일 GameObject 의 Slider 컴포넌트로 체력 비율을 읽는다
        var healthBar = Object.FindFirstObjectByType<HealthBar>();
        Assert.IsNotNull(healthBar, "전제조건: HealthBar 가 씬에 존재해야 함");

        _healthSlider = healthBar.GetComponent<Slider>();
        Assert.IsNotNull(_healthSlider, "전제조건: HealthBar 에 Slider 가 있어야 함");
    }

    /// <summary>체력 수치를 체력바 비율(0.0~1.0)로 환산한다.</summary>
    private float ToHealthRatio(int hitPoints)
    {
        return 1.0f * hitPoints / MaxHitPoints;
    }

    /// <summary>체력바가 기대 비율을 표시하는지 검증한다.</summary>
    private void AssertHealthRatio(float expected, string context)
    {
        Assert.AreEqual(
            expected,
            _healthSlider.value,
            Tolerance,
            $"{context}: 체력바 비율 불일치"
        );
    }

    /// <summary>피격 시 체력바가 데미지만큼 감소하는지 검증한다.</summary>
    private void AssertDamageReducesHealth()
    {
        _player.ApplyDamage(TestDamage);

        AssertHealthRatio(ToHealthRatio(MaxHitPoints - TestDamage), "피격 후");
    }

    /// <summary>회복이 최대 체력을 초과하지 않는지 검증한다.</summary>
    private void AssertHealDoesNotExceedMax()
    {
        _player.ApplyDamage(HeavyDamage);
        AssertHealthRatio(ToHealthRatio(MaxHitPoints - HeavyDamage), "회복 전");

        _player.ApplyHeal(LargeHeal);

        AssertHealthRatio(1.0f, "과다 회복 후");
    }

    /// <summary>데미지 저항 적용 시 피해량이 감소하는지 검증한다.</summary>
    private void AssertDamageResistReducesDamage()
    {
        _player.ApplyDamageResist(DamageResistRate);
        _player.ApplyDamage(TestDamage);

        // 저항 50% 적용 시 실제 피해는 TestDamage 의 절반
        var actualDamage = (int)(TestDamage * (1 - DamageResistRate));

        AssertHealthRatio(ToHealthRatio(MaxHitPoints - actualDamage), "저항 적용 피격 후");
    }


    // ── 3. 메인 실행부 ──────────────────────────────────

    [UnityTest]
    public IEnumerator UT009_피격시_체력바_감소()
    {
        /*
         * [UT-009]
         * 플레이어가 피격되면 체력바가 감소한다
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. 플레이어에게 30 데미지 적용
         *
         * 기대:
         * 체력바가 0.7 을 표시
         */
        yield return LoadBattleScene();

        AssertDamageReducesHealth();
    }


    [UnityTest]
    public IEnumerator UT010_회복시_최대체력_초과_방지()
    {
        /*
         * [UT-010]
         * 회복량이 남은 체력을 초과해도 최대치를 넘지 않는다
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. 50 데미지로 체력을 절반으로 감소
         * 3. 100 회복 적용
         *
         * 기대:
         * 체력바가 1.0 에서 고정
         */
        yield return LoadBattleScene();

        AssertHealDoesNotExceedMax();
    }


    [UnityTest]
    public IEnumerator UT011_데미지_저항_적용()
    {
        /*
         * [UT-011]
         * 데미지 저항 적용 시 실제 피해량이 감소한다
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. 데미지 저항 50% 적용
         * 3. 30 데미지 적용
         *
         * 기대:
         * 실제 피해는 15 이므로 체력바가 0.85 를 표시
         */
        yield return LoadBattleScene();

        AssertDamageResistReducesDamage();
    }
}