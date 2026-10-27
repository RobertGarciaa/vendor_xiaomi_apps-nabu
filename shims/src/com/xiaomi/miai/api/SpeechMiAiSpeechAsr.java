/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.miai.api;

import java.util.Collections;
import java.util.List;

/**
 * App-local stand-ins for the Xiaomi miai ASR value types.
 *
 * Data carriers for cloud speech recognition. Nothing is recognized because the
 * service is absent; the constructors are kept so the stock call sites link.
 */
public final class SpeechMiAiSpeechAsr {
    private SpeechMiAiSpeechAsr() {
    }

    /** Audio codec of a recognize request. */
    public enum AsrCodec {
        pcm
    }

    /** One recognized sentence. Empty when nothing was recognized. */
    public static class Sentence {
        private final String lang;
        private final String text;

        public Sentence() {
            this(null, null);
        }

        public Sentence(String text, String lang) {
            this.text = text;
            this.lang = lang;
        }

        public String getLang() {
            return lang;
        }

        public String getText() {
            return text;
        }
    }

    /** A recognize request. Carries no live audio. */
    public static class SpeechRecognize {
        private String deviceType;

        public SpeechRecognize(String deviceId, AsrCodec codec, int sampleRate,
                int channelCount, int bitDepth, List<String> hints) {
            // Data carrier only; no audio session is created.
        }

        public SpeechRecognize setDeviceType(String deviceType) {
            this.deviceType = deviceType;
            return this;
        }

        public String getDeviceType() {
            return deviceType;
        }

        public List<Sentence> getSentences() {
            return Collections.emptyList();
        }
    }
}
