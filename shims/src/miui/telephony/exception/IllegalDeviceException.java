/* SPDX-License-Identifier: Apache-2.0 */
package miui.telephony.exception;

/**
 * App-local stand-in for MIUI's miui.telephony.exception.IllegalDeviceException.
 *
 * Constructed in the cloud telephony path. Keeping the real exception type means
 * callers that catch it still behave correctly instead of failing with
 * NoClassDefFoundError.
 */
public class IllegalDeviceException extends Exception {
    private static final long serialVersionUID = 1L;

    public IllegalDeviceException() {
        super();
    }

    public IllegalDeviceException(String message) {
        super(message);
    }

    public IllegalDeviceException(String message, Throwable cause) {
        super(message, cause);
    }
}
