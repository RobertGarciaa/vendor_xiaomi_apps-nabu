/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.miai.api.common;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.miai.api.common.Instruction.
 *
 * A parsed cloud-AI instruction. The miai service is unavailable, so nothing is
 * ever parsed and the accessors report empty values.
 */
public class Instruction {
    private final String name;
    private final Object payload;

    public Instruction() {
        this(null, null);
    }

    public Instruction(String name, Object payload) {
        this.name = name;
        this.payload = payload;
    }

    public String getName() {
        return name;
    }

    public Object getPayload() {
        return payload;
    }
}
