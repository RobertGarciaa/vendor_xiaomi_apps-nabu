/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.common;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.common.Optional.
 *
 * The stock class is a small Optional used by the miai transport classes. This
 * port needs a working implementation because the app inspects isPresent()
 * before calling get(). It is a faithful, dependency-free Optional; it does not
 * pretend a value exists.
 */
public final class Optional<T> {
    private static final Optional<?> EMPTY = new Optional<>(null, false);

    private final T value;
    private final boolean present;

    private Optional(T value, boolean present) {
        this.value = value;
        this.present = present;
    }

    public static <T> Optional<T> empty() {
        @SuppressWarnings("unchecked")
        Optional<T> empty = (Optional<T>) EMPTY;
        return empty;
    }

    public static <T> Optional<T> of(T value) {
        return new Optional<>(java.util.Objects.requireNonNull(value), true);
    }

    public static <T> Optional<T> ofNullable(T value) {
        return value == null ? empty() : of(value);
    }

    public boolean isPresent() {
        return present;
    }

    public T get() {
        if (!present) {
            throw new java.util.NoSuchElementException("Optional is empty");
        }
        return value;
    }

    public T orElse(T fallback) {
        return present ? value : fallback;
    }

    @Override
    public String toString() {
        return present ? "Optional[" + value + "]" : "Optional.empty";
    }
}
