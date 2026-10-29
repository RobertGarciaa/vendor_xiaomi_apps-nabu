package org.pixelos.nabu.apps;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.Button;
import android.widget.TextView;

/** Local replacement for Xiaomi's unavailable consent activity; grants no permissions. */
public final class CreationConsentActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        setTheme(android.R.style.Theme_DeviceDefault_Light);
        super.onCreate(state);
        boolean ko = getResources().getConfiguration().getLocales().get(0).getLanguage().equals("ko");
        LinearLayout view = new LinearLayout(this);
        view.setOrientation(LinearLayout.VERTICAL);
        int padding = (int)(24 * getResources().getDisplayMetrics().density);
        view.setPadding(padding, padding, padding, padding);
        TextView purpose = new TextView(this);
        purpose.setText(getIntent().getStringExtra("all_purpose"));
        view.addView(purpose);
        String[] keys = {"user_agreement", "privacy_policy"};
        String[] labels = ko ? new String[]{"사용자 약관", "개인정보 처리방침"}
                : new String[]{"User agreement", "Privacy policy"};
        for (int i=0; i<keys.length; i++) {
            String url = getIntent().getStringExtra(keys[i]);
            if (url == null || !url.startsWith("https://privacy.mi.com/")) continue;
            Button button = new Button(this);
            button.setText(labels[i]);
            button.setOnClickListener(v -> {
                Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                if (intent.resolveActivity(getPackageManager()) != null) startActivity(intent);
            });
            view.addView(button);
        }
        new AlertDialog.Builder(this)
            .setTitle(ko ? "Xiaomi Creation 사용 안내" : "Xiaomi Creation")
            .setView(view)
            .setPositiveButton(ko ? "동의" : "Agree", (d,w) -> { setResult(1); finish(); })
            .setNegativeButton(ko ? "동의하지 않음" : "Decline", (d,w) -> { setResult(0); finish(); })
            .setOnCancelListener(d -> { setResult(0); finish(); })
            .show();
    }
}
