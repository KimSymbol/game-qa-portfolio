// 역할: 씬 로드 및 기본 오브젝트 존재 검증 (UT-001 ~ UT-002)

using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;


public class SceneLoadTest
{
    // ── 1. 변수 선언부 ──────────────────────────────────

    private const string TitleSceneName = "TitleScene";
    private const string BattleSceneName = "BattleScene";

    // 씬 로드 후 오브젝트 초기화 대기 시간
    private const float SceneReadyDelay = 0.5f;


    // ── 2. 함수 선언부 ──────────────────────────────────

    /// <summary>지정한 씬을 로드하고 초기화를 기다린다.</summary>
    private IEnumerator LoadScene(string sceneName)
    {
        // batchmode(CI)에는 입력 장치가 없어 OnScreenControl 이 예외를 던진다.
        // 테스트 대상 로직과 무관한 환경 제약이므로 무시한다.
        LogAssert.ignoreFailingMessages = true;

        yield return SceneManager.LoadSceneAsync(sceneName);
        yield return new WaitForSeconds(SceneReadyDelay);
    }

    /// <summary>현재 활성 씬이 기대한 씬인지 검증한다.</summary>
    private void AssertActiveScene(string expected)
    {
        Assert.AreEqual(
            expected,
            SceneManager.GetActiveScene().name,
            $"활성 씬이 {expected} 가 아님"
        );
    }

    /// <summary>씬에 지정 타입의 오브젝트가 존재하는지 검증한다.</summary>
    private void AssertObjectExists<T>() where T : Object
    {
        var found = Object.FindFirstObjectByType<T>();

        Assert.IsNotNull(found, $"{typeof(T).Name} 오브젝트가 씬에 없음");
    }


    // ── 3. 메인 실행부 ──────────────────────────────────

    [UnityTest]
    public IEnumerator UT001_타이틀씬_로드()
    {
        /*
         * [UT-001]
         * 타이틀 씬 로드
         *
         * 절차:
         * 1. TitleScene 로드
         *
         * 기대:
         * 활성 씬이 TitleScene 으로 전환됨
         */
        yield return LoadScene(TitleSceneName);

        AssertActiveScene(TitleSceneName);
    }


    [UnityTest]
    public IEnumerator UT002_배틀씬_플레이어_존재()
    {
        /*
         * [UT-002]
         * 배틀 씬 진입 시 플레이어 생성 확인
         *
         * 절차:
         * 1. BattleScene 로드
         *
         * 기대:
         * 활성 씬이 BattleScene 이며 Player 오브젝트가 존재
         */
        yield return LoadScene(BattleSceneName);

        AssertActiveScene(BattleSceneName);
        AssertObjectExists<Player>();
    }
}