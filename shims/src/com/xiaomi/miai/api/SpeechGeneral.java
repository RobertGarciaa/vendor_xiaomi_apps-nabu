/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.miai.api;

import java.util.Collections;
import java.util.List;

/**
 * App-local stand-ins for the Xiaomi miai speech API value types.
 *
 * Notes and Creation reference these classes only as data carriers for cloud
 * speech recognition. No miai service exists on PixelOS, so the carriers hold
 * nothing and every getter returns an empty or null value. No transcription is
 * fabricated.
 */
public final class SpeechGeneral {
    private SpeechGeneral() {
    }

    /** Emitted when a recognize stream ends. Carries no state. */
    public static class RecognizeStreamEnded {
        public RecognizeStreamEnded() {
        }
    }

    /** Emitted when a recognize stream starts. Carries no state. */
    public static class RecognizeStreamStarted {
        public RecognizeStreamStarted() {
        }
    }

    /** Recognizer vendor. Kept for source compatibility. */
    public enum Vendor {
        XiaoMi
    }
}
