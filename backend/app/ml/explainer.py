class RiskExplainer:
    @staticmethod
    def generate_reasons_for_user(feature_row):
        """
        Evaluates a single user's feature values dict and returns a list of human-readable
        explainability reasons.
        """
        reasons = []

        after_hours_ratio = feature_row.get('after_hours_ratio', 0.0)
        failed_logins = feature_row.get('failed_login_count', 0)
        file_count = feature_row.get('file_access_count', 0)
        download_mb = feature_row.get('download_volume_mb', 0.0)
        upload_mb = feature_row.get('upload_volume_mb', 0.0)
        loc_deviations = feature_row.get('location_deviation_count', 0)
        dev_deviations = feature_row.get('device_deviation_count', 0)

        if after_hours_ratio > 0.20:
            pct = int(after_hours_ratio * 100)
            reasons.append(f"Unusual after-hours activity ({pct}% of recorded events outside standard hours)")

        if failed_logins >= 3:
            reasons.append(f"Multiple failed login attempts detected ({failed_logins} failed attempts over the analysis period)")
        elif failed_logins >= 1:
            reasons.append(f"Occasional login authentication failures ({failed_logins} failed attempt{'s' if failed_logins != 1 else ''} over the analysis period)")

        if download_mb > 300.0:
            reasons.append(f"Download volume significantly above baseline ({download_mb:.1f} MB downloaded)")
        elif download_mb > 100.0:
            reasons.append(f"Elevated file download volume ({download_mb:.1f} MB downloaded)")

        if upload_mb > 100.0:
            reasons.append(f"Abnormally high data egress / upload volume ({upload_mb:.1f} MB uploaded)")
        elif upload_mb > 30.0:
            reasons.append(f"Elevated outbound data transfer ({upload_mb:.1f} MB uploaded)")

        if loc_deviations >= 1:
            reasons.append("Geographic location deviation (login attempt outside primary office region)")

        if dev_deviations >= 1:
            reasons.append("Device hardware deviation (access from unregistered MAC / endpoint)")

        if file_count > 35:
            reasons.append(f"High file access volume ({file_count} files accessed over the analysis period)")

        if not reasons:
            reasons.append("Behavior consistent with standard employee baseline profile")

        return reasons
