# 의존성 조사 — 메모 / Creation

조사일: 2026-10-27
원본: `shuntian-ota_full-OS4.0.9.0.XFPCNXM-user-17.0-6312ae8075`
(미패드9 프로, HyperOS 4, Android 17 / SDK 37)

## 요약

| 앱 | 패키지 | 버전 | MIUI/Xiaomi 클래스 참조 | shim 필요 |
| --- | --- | --- | --- | --- |
| 메모 | `com.miui.notes` | 3.2.7.4 (3274) | 81 | 예 |
| Creation | `com.miui.creation` | 4.1.6 (416) | 54 | 예 |


측정 방법: 앱의 `classes*.dex`를 smali로 디코딩한 뒤, 문자열 리터럴을 제외하고
실제 `invoke-*`/`sget`/`sput`/`new-instance`/`.super`/`.implements`에 등장하는
MIUI·Xiaomi·miuix 타입만 집계했다. `com/miui/notes` 처럼 앱이 스스로 정의한
클래스는 제외했다.

## 메모 (com.miui.notes)

### 의존성 분포

| 제공처 | 개수 | 처리 |
| --- | --- | --- |
| PixelOS `framework.jar`에 이미 존재 | 2 | 그대로 사용 |
| shuntian `miui-framework.jar` 전용 | 12 | 앱 로컬 shim |
| 샤오미 시스템 앱 전용 | 67 | 앱 로컬 shim |

PixelOS가 이미 제공하는 것:
- `com/android/internal/view/menu/MenuBuilder`
- `com/android/internal/graphics/drawable/BackgroundBlurDrawable`

`miui-framework.jar`에서 오는 것:
- `miui.os.Build`
- `miui.os.UserHandle`
- `miui.util.HapticFeedbackUtil`, `FeatureParser`, `HashUtils`, `AppConstants`
- `miui.content.res.IconCustomizer`, `ThemeResources`, `ThemeResourcesSystem`,
  `ThemeNativeUtils`
- `miui.accounts.ExtraAccountManager`
- `miui.app.backup.BackupManager`, `BackupMeta`, `FullBackupAgent`
- `com.xiaomi.mimotion.MimotionUtils`

샤오미 시스템 앱에만 있는 것(앱 로컬 shim으로 대체):
- Xiaomi OAuth (`com.xiaomi.account.openauth.*`)
- privacy getter 18종 (`com.xiaomi.account.privacy_data.*`)
- miai 음성 API (`com.xiaomi.miai.api.*`)
- micloud SDK (`com.xiaomi.micloudsdk.*`)
- settingsdk backup (`com.xiaomi.settingsdk.backup.*`)
- cloud sync provider 12종 (`miui.cloud.sync.providers.*`)
- `miui.app.IMiuiFreeFormManager`

### 앱이 직접 상속하는 외부 클래스

이 셋은 shim이 **정확한 계층**을 가져야 한다. 그렇지 않으면 클래스 로딩이 실패한다.

| 앱 클래스 | 외부 부모 |
| --- | --- |
| `com.miui.notes.backup.NoteBackupAgent` | `miui.app.backup.FullBackupAgent` |
| `com.miui.notes.backup.NoteSettingsBackupService` | `com.xiaomi.settingsdk.backup.CloudBackupServiceBase` |
| `tx/a`, `tx/b`, `tx/c` | `miui.cloud.sync.SyncInfoProviderBase` |

`SyncInfoProvider`는 **인터페이스**이고 `SyncInfoProviderBase`는 **클래스**다.
`ir/f`가 `SyncInfoProvider`로 캐스팅한 뒤 null 검사하므로, provider가 없으면
아무 값도 보고하지 않는다.

### IS_TABLET

renoIR 포팅은 `Lmiui/os/Build;->IS_TABLET:Z` 87곳을 전부 `const/4 0x0`으로
치환해 태블릿 UI를 껐다. renoir 배포 APK의 dex에는 `miui/os/Build` 참조가 0개다.

nabu는 `ro.build.characteristics=tablet`인 태블릿이므로 정반대다.
이 포팅의 shim은 값을 상수로 박지 않고 실제 시스템 속성에서 읽는다.

```java
public static final boolean IS_TABLET = isTablet();  // ro.build.characteristics
```

## Creation (com.miui.creation)

MIUI 의존성 54개 중 대부분이 클라우드 동기화다.

- `miui.cloud.sync.*`, `miui.cloud.util.*`, `miui.cloud.telephony.*`
- `com.xiaomi.micloudsdk.*`
- `com.miui.aiengine.common.cloud.GetDownloadFileUrlFailedStatParam` (통계 1건)
- `miui.os.Build`, `miui.os.UserHandle`, `miui.securityspace.CrossUserUtils`
- `miui.util.HapticFeedbackUtil`, `FeatureParser`

Creation은 메모와 `libnotes_algorithm.so`를 공유하므로 메모를 먼저 완성했다.

### privileged 권한

Creation은 `INTERNAL_SYSTEM_WINDOW`(protectionLevel `signature|module|recents`)를
선언하므로 `product/priv-app`에 배치하고 allowlist를 둔다.
`READ_FRAME_BUFFER`와 `SYSTEM_OVERLAY_WINDOW`는 signature 권한이라 플랫폼
서명만으로 부여되며 privapp allowlist 대상이 아니다.

## 재현

```sh
# 원본 고정 확인
python3 tools/extract-sources.py --verify-only

# shim 컴파일 + 커버리지 검사
python3 tools/build-shims.py --rom-root /path/to/pixelos \
    --app-smali /path/to/decoded/MIUINotes-smali



# 종합 검증
python3 tools/verify-apps.py --rom-root /path/to/pixelos
```
