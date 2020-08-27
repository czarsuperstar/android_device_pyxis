#
# Copyright (C) 2020 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

import hashlib
import common
import re

def FullOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def IncrementalOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def FullOTA_Assertions(info):
  AddModemAssertion(info, info.input_zip)
  return

def IncrementalOTA_Assertions(info):
  AddModemAssertion(info, info.target_zip)
  return

def AddImage(info, basename, dest):
  path = "IMAGES/" + basename
  if path not in info.input_zip.namelist():
    return

  data = info.input_zip.read(path)
  common.ZipWriteStr(info.output_zip, basename, data)
  info.script.Print("Patching {} image unconditionally...".format(dest.split('/')[-1]))
  info.script.AppendExtra('package_extract_file("%s", "%s");' % (basename, dest))

def OTA_InstallEnd(info):
  AddImage(info, "dtbo.img", "/dev/block/bootdevice/by-name/dtbo")
  return

def AddModemAssertion(info, input_zip):
  android_info = info.input_zip.read("OTA/android-info.txt")
  m = re.search(r'require\s+version-modem\s*=\s*(.+)', android_info)
  miui_version = re.search(r'require\s+version-miui\s*=\s*(.+)', android_info)
  if m and miui_version:
    timestamp = m.group(1).rstrip()
    firmware_version = miui_version.group(1).rstrip()
    if ((len(timestamp) and '*' not in timestamp) and \
        (len(firmware_version) and '*' not in firmware_version)):
      cmd = 'assert(xiaomi.verify_modem("{}") == "1" || abort("ERROR: This package requires firmware from MIUI {} developer build or newer. Please upgrade firmware and retry!"););'
      info.script.AppendExtra(cmd.format(timestamp, firmware_version))
  return
