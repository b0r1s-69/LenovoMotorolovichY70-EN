#!/usr/bin/env python3
"""Add the battery charge limit feature to the decoded v3.2 tree."""
import re, io, sys

DEC = '/home/admin1/apk-en/v32/dec'

# ---------------------------------------------------------------- 1. strings
STRINGS = {
 'cl_title': 'Battery charge limit',
 'cl_badge': 'Root',
 'cl_desc': ('• Stops charging when the battery reaches the level you pick, then resumes a few '
             'percent below it\\n• Drives the charging circuit node directly — needs root '
             '(Magisk / KernelSU)\\n• Keeps the battery in its comfortable range and cuts wear on '
             'overnight charges'),
 'cl_status_off': 'Limit: Off • charging to 100%',
 'cl_off': 'Off',
 'cl_80': '80%',
 'cl_85': '85%',
 'cl_90': '90%',
 'cl_95': '95%',
 'cl_footer': ('💡 No root? Moto Battery Care can cap charging at 80% — open it with the button '
               'above.'),
}
p = f'{DEC}/res/values/strings.xml'
s = open(p, encoding='utf-8').read()
if 'name="cl_title"' not in s:
    add = ''.join('\n    <string name="%s">%s</string>' % (k, v) for k, v in STRINGS.items())
    s = s.replace('</resources>', add + '\n</resources>')
    open(p, 'w', encoding='utf-8').write(s)
    print('strings: added', len(STRINGS))

# ---------------------------------------------------------------- 2. layout
CARD = '''        <LinearLayout android:orientation="vertical" android:id="@+id/card_charge_limit" android:background="@drawable/card_bg" android:padding="16.0dp" android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="14.0dp">
            <LinearLayout android:gravity="center_vertical" android:orientation="horizontal" android:layout_width="match_parent" android:layout_height="wrap_content">
                <ImageView android:layout_width="22.0dp" android:layout_height="22.0dp" android:src="@drawable/ic_cat_power" android:layout_marginEnd="8.0dp" />
                <TextView android:textSize="17.0sp" android:textStyle="bold" android:textColor="@color/text_primary" android:layout_width="0.0dp" android:layout_height="wrap_content" android:text="@string/cl_title" android:layout_weight="1.0" />
                <TextView android:textSize="11.0sp" android:textStyle="bold" android:textColor="@color/accent_yellow" android:background="@drawable/btn_chip" android:paddingTop="3.0dp" android:paddingBottom="3.0dp" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="@string/cl_badge" android:paddingStart="8.0dp" android:paddingEnd="8.0dp" />
            </LinearLayout>
            <TextView android:textSize="13.0sp" android:textColor="@color/text_secondary" android:layout_width="wrap_content" android:layout_height="wrap_content" android:layout_marginTop="8.0dp" android:text="@string/cl_desc" android:lineSpacingExtra="3.0dp" />
            <LinearLayout android:orientation="vertical" android:background="#151921" android:padding="12.0dp" android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="12.0dp">
                <TextView android:textSize="13.0sp" android:textStyle="bold" android:textColor="@color/accent_green" android:id="@+id/tv_cl_status" android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="@string/cl_status_off" />
            </LinearLayout>
            <LinearLayout android:orientation="horizontal" android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="10.0dp">
                <Button android:textSize="12.0sp" android:textStyle="bold" android:textColor="@color/text_primary" android:gravity="center" android:id="@+id/btn_cl_off" android:background="@drawable/btn_chip" android:paddingTop="8.0dp" android:paddingBottom="8.0dp" android:layout_width="0.0dp" android:layout_height="wrap_content" android:minHeight="42.0dp" android:text="@string/cl_off" android:layout_weight="1.0" android:textAllCaps="false" android:paddingStart="4.0dp" android:paddingEnd="4.0dp" android:layout_marginEnd="3.0dp" />
                <Button android:textSize="12.0sp" android:textStyle="bold" android:textColor="#ffffff" android:gravity="center" android:id="@+id/btn_cl_80" android:background="@drawable/btn_primary" android:paddingTop="8.0dp" android:paddingBottom="8.0dp" android:layout_width="0.0dp" android:layout_height="wrap_content" android:minHeight="42.0dp" android:text="@string/cl_80" android:layout_weight="1.0" android:textAllCaps="false" android:paddingStart="4.0dp" android:paddingEnd="4.0dp" android:layout_marginStart="3.0dp" android:layout_marginEnd="3.0dp" />
                <Button android:textSize="12.0sp" android:textStyle="bold" android:textColor="@color/text_primary" android:gravity="center" android:id="@+id/btn_cl_85" android:background="@drawable/btn_chip" android:paddingTop="8.0dp" android:paddingBottom="8.0dp" android:layout_width="0.0dp" android:layout_height="wrap_content" android:minHeight="42.0dp" android:text="@string/cl_85" android:layout_weight="1.0" android:textAllCaps="false" android:paddingStart="4.0dp" android:paddingEnd="4.0dp" android:layout_marginStart="3.0dp" android:layout_marginEnd="3.0dp" />
                <Button android:textSize="12.0sp" android:textStyle="bold" android:textColor="@color/text_primary" android:gravity="center" android:id="@+id/btn_cl_90" android:background="@drawable/btn_chip" android:paddingTop="8.0dp" android:paddingBottom="8.0dp" android:layout_width="0.0dp" android:layout_height="wrap_content" android:minHeight="42.0dp" android:text="@string/cl_90" android:layout_weight="1.0" android:textAllCaps="false" android:paddingStart="4.0dp" android:paddingEnd="4.0dp" android:layout_marginStart="3.0dp" android:layout_marginEnd="3.0dp" />
                <Button android:textSize="12.0sp" android:textStyle="bold" android:textColor="@color/text_primary" android:gravity="center" android:id="@+id/btn_cl_95" android:background="@drawable/btn_chip" android:paddingTop="8.0dp" android:paddingBottom="8.0dp" android:layout_width="0.0dp" android:layout_height="wrap_content" android:minHeight="42.0dp" android:text="@string/cl_95" android:layout_weight="1.0" android:textAllCaps="false" android:paddingStart="4.0dp" android:paddingEnd="4.0dp" android:layout_marginStart="3.0dp" />
            </LinearLayout>
            <TextView android:textSize="11.0sp" android:textColor="@color/text_muted" android:layout_width="match_parent" android:layout_height="wrap_content" android:layout_marginTop="8.0dp" android:text="@string/cl_footer" android:lineSpacingExtra="2.0dp" />
        </LinearLayout>
'''
p = f'{DEC}/res/layout/activity_power.xml'
s = open(p, encoding='utf-8').read()
if 'card_charge_limit' not in s:
    marker = '    </LinearLayout>\n</ScrollView>'
    assert marker in s, 'layout anchor missing'
    s = s.replace(marker, CARD + marker)
    open(p, 'w', encoding='utf-8').write(s)
    print('layout: card inserted')

# ---------------------------------------------------------------- 3. manifest
p = f'{DEC}/AndroidManifest.xml'
s = open(p, encoding='utf-8').read()
if 'ChargeLimitService' not in s:
    anchor = '''        <service android:exported="false" android:foregroundServiceType="specialUse" android:name=".AodTimeoutService">
            <property android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE" android:value="aod_timeout_fade_timer"/>
        </service>'''
    assert anchor in s, 'manifest anchor missing'
    svc = anchor + '''
        <service android:exported="false" android:foregroundServiceType="specialUse" android:name=".ChargeLimitService">
            <property android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE" android:value="battery_charge_limit_enforcement"/>
        </service>'''
    s = s.replace(anchor, svc)
    open(p, 'w', encoding='utf-8').write(s)
    print('manifest: service registered')

# ---------------------------------------------------------------- 4. activity wiring
p = f'{DEC}/smali/com/moto/resolutionmaster/PowerActivity.smali'
s = open(p, encoding='utf-8').read()
if 'ChargeLimitBridge' not in s:
    old = '''    :cond_0
    invoke-direct {p0}, Lcom/moto/resolutionmaster/PowerActivity;->setupControls()V

    .line 35
    return-void'''
    new = '''    :cond_0
    invoke-direct {p0}, Lcom/moto/resolutionmaster/PowerActivity;->setupControls()V

    invoke-static {p0}, Lcom/moto/resolutionmaster/ChargeLimitBridge;->bind(Landroid/app/Activity;)V

    .line 35
    return-void'''
    assert old in s, 'PowerActivity anchor missing'
    s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)
    print('PowerActivity: bridge wired')
print('done')
