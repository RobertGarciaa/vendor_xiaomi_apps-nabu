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

PRODUCT_PACKAGES += \
    MIUINotes \
    Creation

# Privileged-permission allowlists must live on the same partition as the app.
# Both privileged apps are installed to product/priv-app, so the allowlists go
# to product/etc/permissions.
PRODUCT_COPY_FILES += \
    vendor/xiaomi/apps-nabu/configs/privapp-permissions-miuinotes.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/privapp-permissions-miuinotes.xml \
    vendor/xiaomi/apps-nabu/configs/privapp-permissions-creation.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/permissions/privapp-permissions-creation.xml

endif # TARGET_ENABLE_XIAOMI_APPS
