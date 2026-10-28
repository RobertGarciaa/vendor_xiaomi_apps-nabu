# SPDX-License-Identifier: Apache-2.0
#
# Board configuration for the Ported Xiaomi apps.
#
# Include this from the nabu BoardConfig.mk:
#   include vendor/xiaomi/apps-nabu/BoardConfig.mk
#
# No SELinux policy is added: all three apps use the platform_app domain
# family under the stock AOSP rules. No new
# domains, file types or vendor properties are introduced.

ifeq ($(TARGET_ENABLE_XIAOMI_APPS),true)
# The stock apps target SDK 35/36 and use their own bundled Gson, so no
# platform compatibility libraries are needed.
endif
