# SPDX-License-Identifier: Apache-2.0
LOCAL_PATH := $(call my-dir)

# Qt uses ApplicationInfo.nativeLibraryDir, requiring installed JNI files.
# Keep ELF files out of PRODUCT_COPY_FILES and use the standard app installer.
define nabu-qt-prebuilt
include $$(CLEAR_VARS)
LOCAL_MODULE := $(1)
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_SUFFIX := $$(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_MODULE_TAGS := optional
LOCAL_PRODUCT_MODULE := true
LOCAL_MODULE_TARGET_ARCH := arm64
LOCAL_MULTILIB := 64
LOCAL_CERTIFICATE := platform
LOCAL_DEX_PREOPT := false
LOCAL_SRC_FILES := proprietary/ported/product/app/$(1)/$(1).apk
LOCAL_PREBUILT_JNI_LIBS := $$(patsubst $$(LOCAL_PATH)/%,%,$$(wildcard $$(LOCAL_PATH)/proprietary/native/$(1)/*.so))
ifeq ($$(strip $$(LOCAL_PREBUILT_JNI_LIBS)),)
$$(error $(1): missing JNI payload; run tools/prepare-native.py)
endif
include $$(BUILD_PREBUILT)
endef

$(eval $(call nabu-qt-prebuilt,Creation))
