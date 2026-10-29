"""Route stock consent UI to an in-app activity, preserving explicit user consent."""
from pathlib import Path
import xml.etree.ElementTree as ET

def patch(smali_root, manifest):
    matches=[p for p in smali_root.rglob('*.smali') if 'const-string v1, "com.miui.securitycenter"' in p.read_text() and 'SYSTEM_PERMISSION_DECLARE_NEW' in p.read_text()]
    assert len(matches)==1, f'Unexpected consent helpers: {matches}'
    p=matches[0];s=p.read_text();old='''    const-string v1, "com.miui.securitycenter"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->setPackage(Ljava/lang/String;)Landroid/content/Intent;'''
    new='''    const-string v1, "com.miui.creation"

    const-string v2, "org.pixelos.nabu.apps.CreationConsentActivity"

    invoke-virtual {v0, v1, v2}, Landroid/content/Intent;->setClassName(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;'''
    assert s.count(old)==1;p.write_text(s.replace(old,new))
    ns='http://schemas.android.com/apk/res/android';tree=ET.parse(manifest);app=tree.getroot().find('application');assert app is not None
    ET.SubElement(app,'activity',{f'{{{ns}}}name':'org.pixelos.nabu.apps.CreationConsentActivity',f'{{{ns}}}exported':'false'})
    tree.write(manifest,encoding='utf-8',xml_declaration=True)

    # Keep the object for stock lifecycle code, but remove its visible setting.
    matches=[p for p in smali_root.rglob('*.smali') if '"pref_micloud"' in p.read_text() and '->setOnPreferenceClickListener' in p.read_text() and 'PreferenceMiCloud;' in p.read_text()]
    assert len(matches)==1, f'Unexpected cloud settings fragments: {matches}'
    p=matches[0];s=p.read_text()
    needle='    invoke-virtual {v0, p0}, Landroidx/preference/Preference;->setOnPreferenceClickListener(Landroidx/preference/Preference$OnPreferenceClickListener;)V'
    start=s.index('    const-string v0, \"pref_micloud\"')
    end=s.index('.end method',start)
    head,body,tail=s[:start],s[start:end],s[end:]
    assert body.count(needle)==1
    body=body.replace(needle,needle+'\n\n    const/4 v1, 0x0\n\n    invoke-virtual {v0, v1}, Landroidx/preference/Preference;->setVisible(Z)V')
    p.write_text(head+body+tail)
