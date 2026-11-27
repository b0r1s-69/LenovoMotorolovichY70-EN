package com.moto.resolutionmaster;

import android.content.Context;
import android.content.SharedPreferences;

import java.lang.reflect.Method;

/**
 * Battery charge limit: persistence plus the sysfs plumbing.
 *
 * Two mechanisms, tried in this order:
 *   1. a vendor "level" node (charge_stop_level / charge_control_limit) — hardware stops the
 *      charge itself, no polling needed;
 *   2. a boolean "charging enabled" node, toggled by ChargeLimitService as the battery crosses
 *      the threshold.
 *
 * All shell work goes through the app's own ShellHelper, so the existing root / Shizuku path
 * (and its logging) is reused instead of spawning a second privileged channel.
 */
public final class ChargeLimit {

    static final String PREFS = "charge_limit";
    static final String K_LIMIT = "limit";           // 0 = disabled
    static final String K_TOGGLE_NODE = "toggle_node";
    static final String K_LEVEL_NODE = "level_node";

    /** Boolean nodes: 1 = charging allowed, 0 = stopped (input_suspend is inverted). */
    static final String[] TOGGLE_NODES = {
            "/sys/class/power_supply/battery/battery_charging_enabled",
            "/sys/class/power_supply/battery/charging_enabled",
            "/sys/class/power_supply/battery/charge_disable",
            "/sys/class/power_supply/battery/input_suspend",
            "/sys/class/power_supply/battery/batt_slate_mode",
    };

    /** Level nodes: the number is the charge percentage at which the hardware stops. */
    static final String[] LEVEL_NODES = {
            "/sys/class/power_supply/battery/charge_stop_level",
            "/sys/class/power_supply/battery/charge_control_limit",
            "/sys/class/power_supply/battery/battery_charge_limit",
    };

    private ChargeLimit() {
    }

    static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    static int getLimit(Context c) {
        return prefs(c).getInt(K_LIMIT, 0);
    }

    static void setLimit(Context c, int pct) {
        prefs(c).edit().putInt(K_LIMIT, pct < 0 ? 0 : pct).apply();
    }

    // ---------------------------------------------------------------- shell

    /** stdout of a privileged command, or "" when it could not be run. */
    static String sh(Context c, String cmd) {
        try {
            Class<?> cls = Class.forName("com.moto.resolutionmaster.ShellHelper");
            Method m = cls.getMethod("runCommandWithOutput", Context.class, String.class);
            Object r = m.invoke(null, c, cmd);
            return r == null ? "" : r.toString();
        } catch (Throwable t) {
            return "";
        }
    }

    static boolean shRun(Context c, String cmd) {
        try {
            Class<?> cls = Class.forName("com.moto.resolutionmaster.ShellHelper");
            Method m = cls.getMethod("runCommand", Context.class, String.class);
            Object r = m.invoke(null, c, cmd);
            return (r instanceof Boolean) && (Boolean) r;
        } catch (Throwable t) {
            return false;
        }
    }

    static boolean hasRoot(Context c) {
        return sh(c, "id").contains("uid=0");
    }

    /** True when at least one privileged channel answered at all. */
    static boolean hasPrivilege(Context c) {
        String out = sh(c, "id");
        return out.contains("uid=0") || out.contains("uid=2000");
    }

    static String findWritable(Context c, String[] candidates, String cacheKey) {
        SharedPreferences p = prefs(c);
        String cached = p.getString(cacheKey, "");
        if (cached != null && cached.length() > 0 && sh(c, "test -w " + cached + " && echo y").contains("y")) {
            return cached;
        }
        for (String node : candidates) {
            if (sh(c, "test -w " + node + " && echo y").contains("y")) {
                p.edit().putString(cacheKey, node).apply();
                return node;
            }
        }
        return null;
    }

    // ------------------------------------------------------------- control

    /**
     * Asks the hardware to stop at {@code pct} through a level node.
     * Returns true when a node accepted the value — no monitoring is then required.
     */
    static boolean applyLevelNode(Context c, int pct) {
        String node = findWritable(c, LEVEL_NODES, K_LEVEL_NODE);
        if (node == null) {
            return false;
        }
        if (!shRun(c, "echo " + pct + " > " + node)) {
            return false;
        }
        return sh(c, "cat " + node).trim().startsWith(String.valueOf(pct));
    }

    /** Toggles charging through a boolean node. */
    static boolean setChargingEnabled(Context c, boolean enable) {
        String node = findWritable(c, TOGGLE_NODES, K_TOGGLE_NODE);
        if (node == null) {
            return false;
        }
        int value;
        if (node.endsWith("input_suspend") || node.endsWith("charge_disable")) {
            value = enable ? 0 : 1;   // inverted nodes: 1 means "stop"
        } else {
            value = enable ? 1 : 0;
        }
        return shRun(c, "echo " + value + " > " + node);
    }

    /** True when a level node is driving the limit itself (no service needed). */
    static boolean isHardwareMode(Context c, int pct) {
        String node = findWritable(c, LEVEL_NODES, K_LEVEL_NODE);
        if (node == null) {
            return false;
        }
        String cur = sh(c, "cat " + node).trim();
        return cur.startsWith(String.valueOf(pct));
    }

    /** Restores unrestricted charging and clears the stored limit. */
    static void clear(Context c) {
        setLimit(c, 0);
        String levelNode = findWritable(c, LEVEL_NODES, K_LEVEL_NODE);
        if (levelNode != null) {
            shRun(c, "echo 100 > " + levelNode);
        }
        setChargingEnabled(c, true);
    }

    static String activeNode(Context c) {
        String toggle = findWritable(c, TOGGLE_NODES, K_TOGGLE_NODE);
        if (toggle != null) {
            return toggle;
        }
        return findWritable(c, LEVEL_NODES, K_LEVEL_NODE);
    }
}
