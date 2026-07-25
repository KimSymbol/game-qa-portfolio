// 역할: 무기 업그레이드 배율 검증 (UT-006 ~ UT-008)

using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;


public class WeaponUpgradeTest
{
    // ── 1. 변수 선언부 ──────────────────────────────────

    private const string BattleSceneName = "BattleScene";

    // 씬 로드 후 오브젝트 초기화 대기 시간
    private const float SceneReadyDelay = 0.5f;

    // 데미지 업그레이드 레벨별 기대 배율
    private const float DamageLevel1 = 1.3f;
    private const float DamageLevel2 = 1.6f;
    private const float DamageLevel3 = 2.0f;

    // 쿨다운 업그레이드 레벨별 기대 배율 (낮을수록 빠름)
    private const float CooldownLevel1 = 0.8f;
    private const float CooldownLevel2 = 0.6f;
    private const float CooldownLevel3 = 0.3f;

    // 정의되지 않은 레벨 (경계값 검증용)
    private const int UndefinedLevel = 99;

    // float 비교 허용 오차
    private const float Tolerance = 0.001f;

    private WeaponManager _weaponManager;


    // ── 2. 함수 선언부 ──────────────────────────────────

    /// <summary>BattleScene 로드 후 WeaponManager 를 확보한다.</summary>
    private IEnumerator LoadBattleScene()
    {
        // batchmode(CI) 환경에는 입력 장치가 없어 OnScreenControl 이 예외를 던진다.
        // 테스트 대상 로직과 무관한 환경 제약이므로 무시한다.
        LogAssert.ignoreFailingMessages = true;

        yield return SceneManager.LoadSceneAsync(BattleSceneName);
        yield return new WaitForSeconds(SceneReadyDelay);

        _weaponManager = Object.FindFirstObjectByType<WeaponManager>();
        Assert.IsNotNull(_weaponManager, "전제조건: WeaponManager 가 씬에 존재해야 함");
    }

    /// <summary>데미지 업그레이드 후 배율이 기대값과 일치하는지 검증한다.</summary>
    private void AssertDamageModifier(int level, float expected)
    {
        _weaponManager.UpgradeDamage(level);

        Assert.AreEqual(
            expected,
            _weaponManager.GlobalDamageModifier,
            Tolerance,
            $"레벨 {level} 데미지 배율 불일치"
        );
    }

    /// <summary>쿨다운 업그레이드 후 배율이 기대값과 일치하는지 검증한다.</summary>
    private void AssertCooldownModifier(int level, float expected)
    {
        _weaponManager.UpgradeCooldown(level);

        Assert.AreEqual(
            expected,
            _weaponManager.GlobalCooldownModifier,
            Tolerance,
            $"레벨 {level} 쿨다운 배율 불일치"
        );
    }

    /// <summary>정의되지 않은 레벨 입력 시 배율이 변하지 않는지 검증한다.</summary>
    private void AssertModifierUnchangedOnInvalidLevel()
    {
        var before = _weaponManager.GlobalDamageModifier;

        _weaponManager.UpgradeDamage(UndefinedLevel);

        Assert.AreEqual(
            before,
            _weaponManager.GlobalDamageModifier,
            Tolerance,
            "정의되지 않은 레벨에서 배율이 변경됨"
        );
    }


    // ── 3. 메인 실행부 ──────────────────────────────────

    [UnityTest]
    public IEnumerator UT006_데미지_업그레이드_레벨1()
    {
        /*
         * [UT-006]
         * 데미지 업그레이드 레벨 1 적용
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. UpgradeDamage(1) 호출
         *
         * 기대:
         * GlobalDamageModifier 가 1.3 으로 설정됨
         */
        yield return LoadBattleScene();

        AssertDamageModifier(1, DamageLevel1);
    }


    [UnityTest]
    public IEnumerator UT006_데미지_업그레이드_레벨2()
    {
        /*
         * [UT-006]
         * 데미지 업그레이드 레벨 2 적용
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. UpgradeDamage(2) 호출
         *
         * 기대:
         * GlobalDamageModifier 가 1.6 으로 설정됨
         */
        yield return LoadBattleScene();

        AssertDamageModifier(2, DamageLevel2);
    }


    [UnityTest]
    public IEnumerator UT006_데미지_업그레이드_레벨3()
    {
        /*
         * [UT-006]
         * 데미지 업그레이드 레벨 3 적용
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. UpgradeDamage(3) 호출
         *
         * 기대:
         * GlobalDamageModifier 가 2.0 으로 설정됨
         */
        yield return LoadBattleScene();

        AssertDamageModifier(3, DamageLevel3);
    }


    [UnityTest]
    public IEnumerator UT007_쿨다운_업그레이드_레벨1()
    {
        /*
         * [UT-007]
         * 쿨다운 업그레이드 레벨 1 적용
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. UpgradeCooldown(1) 호출
         *
         * 기대:
         * GlobalCooldownModifier 가 0.8 로 설정됨
         */
        yield return LoadBattleScene();

        AssertCooldownModifier(1, CooldownLevel1);
    }


    [UnityTest]
    public IEnumerator UT007_쿨다운_업그레이드_레벨3()
    {
        /*
         * [UT-007]
         * 쿨다운 업그레이드 최대 레벨 적용
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. UpgradeCooldown(3) 호출
         *
         * 기대:
         * GlobalCooldownModifier 가 0.3 으로 설정됨
         */
        yield return LoadBattleScene();

        AssertCooldownModifier(3, CooldownLevel3);
    }


    [UnityTest]
    public IEnumerator UT008_정의되지_않은_레벨_입력()
    {
        /*
         * [UT-008]
         * 정의 범위를 벗어난 레벨 입력 시 동작 확인
         *
         * 절차:
         * 1. BattleScene 로드
         * 2. UpgradeDamage(99) 호출
         *
         * 기대:
         * 배율이 변경되지 않고 기존 값을 유지
         */
        yield return LoadBattleScene();

        AssertModifierUnchangedOnInvalidLevel();
    }
}