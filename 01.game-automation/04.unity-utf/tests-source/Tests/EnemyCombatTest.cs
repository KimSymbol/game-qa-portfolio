// 역할: 적 피격 및 사망 처리 검증 (UT-003 ~ UT-005)

using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;


public class EnemyCombatTest
{
    // ── 1. 변수 선언부 ──────────────────────────────────

    private const string BattleSceneName = "BattleScene";

    // 씬 로드 후 적 스폰까지 대기 시간
    private const float EnemySpawnDelay = 2.0f;

    // 사망 애니메이션(_deathAnimDuration 0.5초) 완료 대기 시간
    private const float DeathAnimDelay = 1.0f;

    // 사망을 유발하지 않을 소량 데미지
    private const int SmallDamage = 5;

    // 어떤 적이든 확실히 사망시킬 과다 데미지
    private const int OverkillDamage = 9999;


    // ── 2. 함수 선언부 ──────────────────────────────────

    /// <summary>BattleScene 을 로드하고 적이 스폰될 때까지 기다린다.</summary>
    private IEnumerator LoadBattleSceneWithEnemy()
    {
        // batchmode(CI)에는 입력 장치가 없어 OnScreenControl 이 예외를 던진다.
        // 테스트 대상 로직과 무관한 환경 제약이므로 무시한다.
        LogAssert.ignoreFailingMessages = true;

        yield return SceneManager.LoadSceneAsync(BattleSceneName);
        yield return new WaitForSeconds(EnemySpawnDelay);
    }

    /// <summary>씬에서 살아있는 적 하나를 찾아 반환한다.</summary>
    private Enemy FindEnemy()
    {
        var enemy = Object.FindFirstObjectByType<Enemy>();
        Assert.IsNotNull(enemy, "전제조건: 씬에 적이 스폰되어 있어야 함");

        return enemy;
    }

    /// <summary>피격 시 체력이 데미지만큼 정확히 감소하는지 검증한다.</summary>
    private void AssertHitpointsReduced(Enemy enemy, int damage)
    {
        var before = enemy.hitpoints;

        enemy.TakeDamage(damage);

        Assert.AreEqual(
            before - damage,
            enemy.hitpoints,
            $"데미지 {damage} 적용 후 체력 불일치"
        );
    }

    /// <summary>과다 데미지를 받아도 체력이 음수가 되지 않는지 검증한다.</summary>
    private void AssertHitpointsNotNegative(Enemy enemy)
    {
        enemy.TakeDamage(OverkillDamage);

        Assert.AreEqual(0, enemy.hitpoints, "체력이 0 미만으로 내려감");
    }

    /// <summary>사망한 적이 씬에서 제거되는지 검증한다.</summary>
    private IEnumerator AssertEnemyDestroyed(Enemy enemy)
    {
        enemy.TakeDamage(OverkillDamage);
        yield return new WaitForSeconds(DeathAnimDelay);

        // Unity 오브젝트는 Destroy 후 null 비교가 true 가 됨
        Assert.IsTrue(enemy == null, "사망 후에도 적 오브젝트가 남아있음");
    }


    // ── 3. 메인 실행부 ──────────────────────────────────

    [UnityTest]
    public IEnumerator UT003_적_피격시_체력_감소()
    {
        /*
         * [UT-003]
         * 적이 피격되면 체력이 감소한다
         *
         * 절차:
         * 1. BattleScene 로드 후 적 스폰 대기
         * 2. 적에게 5 데미지 적용
         *
         * 기대:
         * 체력이 정확히 5 감소
         */
        yield return LoadBattleSceneWithEnemy();

        AssertHitpointsReduced(FindEnemy(), SmallDamage);
    }


    [UnityTest]
    public IEnumerator UT004_적_체력_음수_방지()
    {
        /*
         * [UT-004]
         * 최대 체력을 초과하는 데미지를 받아도 체력이 음수가 되지 않는다
         *
         * 절차:
         * 1. BattleScene 로드 후 적 스폰 대기
         * 2. 적에게 9999 데미지 적용
         *
         * 기대:
         * 체력이 0 으로 고정
         */
        yield return LoadBattleSceneWithEnemy();

        AssertHitpointsNotNegative(FindEnemy());
    }


    [UnityTest]
    public IEnumerator UT005_적_사망시_오브젝트_제거()
    {
        /*
         * [UT-005]
         * 체력이 0 이 된 적은 씬에서 제거된다
         *
         * 절차:
         * 1. BattleScene 로드 후 적 스폰 대기
         * 2. 적에게 치명적 데미지 적용
         * 3. 사망 애니메이션 완료까지 대기
         *
         * 기대:
         * 적 오브젝트가 파괴됨
         */
        yield return LoadBattleSceneWithEnemy();

        yield return AssertEnemyDestroyed(FindEnemy());
    }
}