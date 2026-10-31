# SPDX-License-Identifier: Apache-2.0
#
# Board configuration for the ported Xiaomi apps.
#
# Include this from the nabu BoardConfig.mk:
#   include vendor/xiaomi/apps-nabu/BoardConfig.mk
#
# No SELinux policy is added: the apps use the platform_app domain family under
# the stock AOSP rules. No new domains, file types or vendor properties are
# introduced, so this file intentionally sets nothing.
