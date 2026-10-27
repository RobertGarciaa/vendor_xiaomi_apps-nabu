/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.miai.api;

import java.util.Collections;
import java.util.List;

/**
 * App-local stand-ins for the Xiaomi miai speech-conference value types.
 *
 * Data carriers for cloud meeting transcription. No conference session exists on
 * PixelOS, so every result is empty. Nothing is transcribed or faked.
 */
public final class SpeechMiAiSpeechConference {
    private SpeechMiAiSpeechConference() {
    }

    /** Service info update event. */
    public static class ConferenceServiceInfoUpdate {
        public ConferenceServiceInfoUpdate(boolean connected, boolean reconnected,
                boolean closed) {
            // Data carrier only; no conference session is created.
        }
    }

    /** One conference recognition result. */
    public static class ConferenceServiceResult {
        public ConferenceServiceResult() {
        }

        public String getDetectedLang() {
            return null;
        }

        public int getSentenceId() {
            return -1;
        }

        public List<Sentence> getSentences() {
            return Collections.emptyList();
        }

        public boolean isSentenceCompleted() {
            return false;
        }
    }

    /** A recognized sentence. */
    public static class Sentence {
        private final String text;
        private final String lang;

        public Sentence() {
            this(null, null);
        }

        public Sentence(String text, String lang) {
            this.text = text;
            this.lang = lang;
        }

        public String getText() {
            return text;
        }

        public String getLang() {
            return lang;
        }
    }

    /** Voice-over result for one sentence. */
    public static class VorResult {
        private final int sentenceId;
        private final String role;

        public VorResult() {
            this(-1, null);
        }

        public VorResult(int sentenceId, String role) {
            this.sentenceId = sentenceId;
            this.role = role;
        }

        public int getSentenceId() {
            return sentenceId;
        }

        public String getVorRole() {
            return role;
        }
    }

    /** Container of voice-over results. */
    public static class SpeechConferenceVorResult {
        public SpeechConferenceVorResult() {
        }

        public List<VorResult> getVorResults() {
            return Collections.emptyList();
        }
    }
}
