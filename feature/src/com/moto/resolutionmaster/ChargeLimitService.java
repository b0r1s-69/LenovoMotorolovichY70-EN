package com.moto.resolutionmaster;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.BatteryManager;
import android.os.Build;
import android.os.IBinder;

/**
 * Enforces the charge limit while the phone is plugged in.
 *
 * Only needed for the toggle-node mechanism: when the battery reaches the limit the charge is
 * stopped, and it is allowed again once the level falls a few percent below it (hysteresis stops
 * the charger from being toggled on every percent). Unplugging restores charging so the next
 * session behaves normally.
 */
public class ChargeLimitService extends Service {

    static final String CHANNEL = "charge_limit";
    static final int NOTIFICATION_ID = 4711;
    /** How far below the limit the battery must fall before charging resumes. */
    static final int HYSTERESIS = 3;

    private BroadcastReceiver receiver;
    private boolean stoppedByUs;

    @Override
    public void onCreate() {
        super.onCreate();
        createChannel();
        receiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                onBatteryChanged(intent);
            }
        };
        registerReceiver(receiver, new IntentFilter(Intent.ACTION_BATTERY_CHANGED));
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        startForeground(NOTIFICATION_ID, buildNotification(getLimit(), -1));
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        if (receiver != null) {
            try {
                unregisterReceiver(receiver);
            } catch (Throwable ignored) {
            }
            receiver = null;
        }
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private int getLimit() {
        return ChargeLimit.getLimit(this);
    }

    private void onBatteryChanged(Intent intent) {
        int limit = getLimit();
        if (limit <= 0) {
            return;
        }
        int level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
        int scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, 100);
        int plugged = intent.getIntExtra(BatteryManager.EXTRA_PLUGGED, 0);
        if (level < 0 || scale <= 0) {
            return;
        }
        int pct = level * 100 / scale;

        if (plugged == 0) {
            // Unplugged: make sure the port is not left disabled for the next session.
            if (stoppedByUs) {
                ChargeLimit.setChargingEnabled(this, true);
                stoppedByUs = false;
            }
            updateNotification(pct, limit);
            return;
        }

        if (pct >= limit && !stoppedByUs) {
            if (ChargeLimit.setChargingEnabled(this, false)) {
                stoppedByUs = true;
            }
        } else if (pct <= limit - HYSTERESIS && stoppedByUs) {
            if (ChargeLimit.setChargingEnabled(this, true)) {
                stoppedByUs = false;
            }
        }
        updateNotification(pct, limit);
    }

    private void createChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            return;
        }
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (nm == null) {
            return;
        }
        NotificationChannel ch = new NotificationChannel(
                CHANNEL, "Charge limit", NotificationManager.IMPORTANCE_LOW);
        ch.setDescription("Keeps the battery below the configured charge limit");
        ch.setShowBadge(false);
        nm.createNotificationChannel(ch);
    }

    private Notification buildNotification(int limit, int pct) {
        Notification.Builder b;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            b = new Notification.Builder(this, CHANNEL);
        } else {
            b = new Notification.Builder(this);
        }
        String text = limit <= 0
                ? "Charge limit is off"
                : (pct < 0 ? "Limit set to " + limit + "%" : pct + "% • limit " + limit + "%");
        b.setContentTitle("Charge limit")
                .setContentText(text)
                .setSmallIcon(android.R.drawable.ic_lock_idle_charging)
                .setOngoing(true);
        Intent open = new Intent();
        open.setClassName(this, "com.moto.resolutionmaster.PowerActivity");
        open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(
                this, 0, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        b.setContentIntent(pi);
        return b.build();
    }

    private void updateNotification(int pct, int limit) {
        try {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (nm != null) {
                nm.notify(NOTIFICATION_ID, buildNotification(limit, pct));
            }
        } catch (Throwable ignored) {
        }
    }
}
