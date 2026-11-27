package com.moto.resolutionmaster;

import android.app.Activity;
import android.app.ActivityManager;
import android.content.Context;
import android.content.Intent;
import android.content.res.Resources;
import android.graphics.Color;
import android.os.BatteryManager;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Glue between the "Battery charge limit" card in activity_power.xml and ChargeLimit / the service.
 * Views are resolved by name so this class needs no R constants and can live in a separate dex.
 */
public final class ChargeLimitBridge {

    private static final String TAG = "ChargeLimit";
    static final int[] PRESETS = {80, 85, 90, 95};

    private ChargeLimitBridge() {
    }

    /** Called from PowerActivity.onCreate. Must never throw into the activity. */
    public static void bind(final Activity a) {
        try {
            final Resources r = a.getResources();
            final String pkg = a.getPackageName();
            final TextView status = (TextView) a.findViewById(
                    r.getIdentifier("tv_cl_status", "id", pkg));
            if (status == null) {
                return;
            }

            View.OnClickListener preset = new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    int pct = presetOf(a, v.getId());
                    apply(a, pct);
                    render(a, status);
                }
            };

            int offId = r.getIdentifier("btn_cl_off", "id", pkg);
            Button off = (Button) a.findViewById(offId);
            if (off != null) {
                off.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        disable(a);
                        render(a, status);
                    }
                });
            }
            for (int pct : PRESETS) {
                Button b = (Button) a.findViewById(r.getIdentifier("btn_cl_" + pct, "id", pkg));
                if (b != null) {
                    b.setOnClickListener(preset);
                }
            }

            render(a, status);
            // refresh once the shell round-trip has had time to answer
            new Handler(Looper.getMainLooper()).postDelayed(new Runnable() {
                @Override
                public void run() {
                    render(a, status);
                }
            }, 1200);
        } catch (Throwable t) {
            Log.e(TAG, "bind failed", t);
        }
    }

    private static int presetOf(Context c, int viewId) {
        Resources r = c.getResources();
        String pkg = c.getPackageName();
        for (int pct : PRESETS) {
            if (r.getIdentifier("btn_cl_" + pct, "id", pkg) == viewId) {
                return pct;
            }
        }
        return 0;
    }

    private static void apply(Context c, int pct) {
        ChargeLimit.setLimit(c, pct);          // the choice is remembered even without root
        if (!ChargeLimit.hasPrivilege(c)) {
            toast(c, "Limit saved — root is required to enforce it");
            return;
        }
        boolean hardware = ChargeLimit.applyLevelNode(c, pct);
        if (hardware) {
            stopService(c);
            toast(c, "Charge limit set to " + pct + "% (hardware)");
        } else {
            if (ChargeLimit.setChargingEnabled(c, true)) {
                startService(c);
                toast(c, "Charge limit set to " + pct + "%");
            } else {
                toast(c, "No writable charging node on this kernel");
            }
        }
    }

    private static void disable(Context c) {
        if (!ChargeLimit.hasPrivilege(c)) {
            ChargeLimit.setLimit(c, 0);
            toast(c, "Charge limit off");
            return;
        }
        ChargeLimit.clear(c);
        stopService(c);
        toast(c, "Charge limit off, charging to 100%");
    }

    private static void startService(Context c) {
        try {
            c.startForegroundService(new Intent(c, ChargeLimitService.class));
        } catch (Throwable t) {
            Log.e(TAG, "start service failed", t);
        }
    }

    private static void stopService(Context c) {
        try {
            c.stopService(new Intent(c, ChargeLimitService.class));
        } catch (Throwable t) {
            Log.e(TAG, "stop service failed", t);
        }
    }

    private static boolean serviceRunning(Context c) {
        try {
            ActivityManager am = (ActivityManager) c.getSystemService(Context.ACTIVITY_SERVICE);
            if (am == null) {
                return false;
            }
            for (ActivityManager.RunningServiceInfo info : am.getRunningServices(Integer.MAX_VALUE)) {
                if (info.service.getClassName().equals(ChargeLimitService.class.getName())) {
                    return true;
                }
            }
        } catch (Throwable ignored) {
        }
        return false;
    }

    private static int batteryPercent(Context c) {
        try {
            BatteryManager bm = (BatteryManager) c.getSystemService(Context.BATTERY_SERVICE);
            if (bm != null) {
                int v = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY);
                if (v >= 0) {
                    return v;
                }
            }
        } catch (Throwable ignored) {
        }
        return -1;
    }

    private static void render(Context c, TextView status) {
        int limit = ChargeLimit.getLimit(c);
        int pct = batteryPercent(c);
        String level = pct < 0 ? "?" : String.valueOf(pct);
        String text;
        int color;
        if (limit <= 0) {
            text = "Limit: Off • charging to 100%";
            color = 0xFF8B93A5;
        } else if (!ChargeLimit.hasPrivilege(c)) {
            text = "Limit: " + limit + "% • root required to enforce • battery " + level + "%";
            color = 0xFFFACC15;
        } else if (ChargeLimit.isHardwareMode(c, limit)) {
            text = "Limit: " + limit + "% • hardware node active • battery " + level + "%";
            color = 0xFF4ADE80;
        } else if (serviceRunning(c)) {
            text = "Limit: " + limit + "% • enforcing • battery " + level + "%";
            color = 0xFF4ADE80;
        } else {
            text = "Limit: " + limit + "% • armed, no writable node • battery " + level + "%";
            color = 0xFFFACC15;
        }
        status.setText(text);
        status.setTextColor(color);
    }

    private static void toast(Context c, String msg) {
        try {
            Toast.makeText(c, msg, Toast.LENGTH_SHORT).show();
        } catch (Throwable ignored) {
        }
    }
}
