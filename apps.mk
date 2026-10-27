# SPDX-License-Identifier: Apache-2.0
#
# Xiaomi Pad 5 stock apps for PixelOS Android 17.
#
# Inherit this from the nabu device.mk after the common tree:
#   $(call inherit-product, vendor/xiaomi/apps-nabu/apps.mk)
#
# Set TARGET_ENABLE_XIAOMI_APPS=false to build without any of these apps.

TARGET_ENABLE_XIAOMI_APPS ?= true

ifeq ($(TARGET_ENABLE_XIAOMI_APPS),true)

PRODUCT_SOONG_NAMESPACES += \
    vendor/xiaomi/apps-nabu

# Notes is privileged; Creation are normal platform-signed product apps.
PRODUCT_PACKAGES += \
    MIUINotes \
    Creation

# Privileged-permission allowlists must live on the same partition as the app.
# Notes is installed to product/priv-app. Creation's signature-only permissions
# do not require priv-app placement or a privileged-permission allowlist.
PRODUCT_COPY_FILES += \
    vendor/xiaomi/apps-nabu/configs/privapp-permissions-miuinotes.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/privapp-permissions-miuinotes.xml

endif # TARGET_ENABLE_XIAOMI_APPS
