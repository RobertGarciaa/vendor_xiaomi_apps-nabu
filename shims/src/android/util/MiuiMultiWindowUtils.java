/* SPDX-License-Identifier: Apache-2.0 */
package android.util;
import java.lang.reflect.Method;
/** Reflection bridge used by the bundled freeform client; absent MIUI APIs return null. */
public final class MiuiMultiWindowUtils {
    private MiuiMultiWindowUtils() {}
    public static Object callStaticObjectMethod(Class<?> owner, Class<?> resultType,
            String name, Class<?>[] parameters, Object[] args) {
        try {
            Method method = owner.getDeclaredMethod(name,
                    parameters == null ? new Class<?>[0] : parameters);
            method.setAccessible(true);
            Object result = method.invoke(null, args == null ? new Object[0] : args);
            return result == null || resultType.isInstance(result) ? result : null;
        } catch (ReflectiveOperationException | RuntimeException unavailable) {
            return null;
        }
    }
    public static Object invoke(Object target, String name, Object[] args) {
        if (target == null) return null;
        // The stock caller only requests the zero-argument MIUI service getter.
        if (args != null && args.length != 0) return null;
        try {
            Method method = target.getClass().getDeclaredMethod(name);
            method.setAccessible(true);
            return method.invoke(target);
        } catch (ReflectiveOperationException | RuntimeException unavailable) {
            return null;
        }
    }
}
