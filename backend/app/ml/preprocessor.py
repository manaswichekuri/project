import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = [
    'after_hours_ratio',
    'failed_login_count',
    'file_access_count',
    'download_volume_mb',
    'upload_volume_mb',
    'location_deviation_count',
    'device_deviation_count'
]

class FeaturePreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False

    def extract_features_from_activities(self, activities, users_map=None):
        """
        Groups raw activity dicts by user_id and computes windowed aggregated features.
        """
        if not activities:
            return pd.DataFrame(columns=['user_id'] + FEATURE_COLUMNS)

        df = pd.DataFrame(activities)

        # Ensure file_details sub-fields are expanded safely
        def parse_file_details(row):
            fd = row.get('file_details') or {}
            return pd.Series({
                'files_cnt': fd.get('files_accessed_count', 0),
                'dl_mb': fd.get('download_size_mb', 0.0),
                'ul_mb': fd.get('upload_size_mb', 0.0)
            })

        expanded_files = df.apply(parse_file_details, axis=1)
        df = pd.concat([df, expanded_files], axis=1)

        # Baseline deviation checks
        if users_map:
            df['is_loc_deviated'] = df.apply(
                lambda r: 1 if r.get('location_name') != users_map.get(r.get('user_id'), {}).get('baseline_location', 'New York, USA') else 0,
                axis=1
            )
            df['is_dev_deviated'] = df.apply(
                lambda r: 1 if r.get('device_id') != users_map.get(r.get('user_id'), {}).get('baseline_device', '') else 0,
                axis=1
            )
        else:
            df['is_loc_deviated'] = df['location_name'].apply(lambda l: 0 if 'USA' in str(l) else 1)
            df['is_dev_deviated'] = df['device_id'].apply(lambda d: 1 if 'UNREGISTERED' in str(d) or 'UNKNOWN' in str(d) else 0)

        # Aggregate by user_id
        grouped = df.groupby('user_id')

        feature_rows = []
        for user_id, group in grouped:
            total_events = len(group)
            after_hours_cnt = group['after_hours'].sum()
            after_hours_ratio = float(after_hours_cnt) / total_events if total_events > 0 else 0.0

            failed_logins = int(group['failed_logins'].sum())
            total_files = int(group['files_cnt'].sum())
            download_mb = float(group['dl_mb'].sum())
            upload_mb = float(group['ul_mb'].sum())
            loc_deviations = int(group['is_loc_deviated'].sum())
            dev_deviations = int(group['is_dev_deviated'].sum())

            feature_rows.append({
                'user_id': user_id,
                'after_hours_ratio': after_hours_ratio,
                'failed_login_count': failed_logins,
                'file_access_count': total_files,
                'download_volume_mb': download_mb,
                'upload_volume_mb': upload_mb,
                'location_deviation_count': loc_deviations,
                'device_deviation_count': dev_deviations
            })

        feature_df = pd.DataFrame(feature_rows)
        return feature_df

    def fit_transform(self, feature_df):
        """Fit StandardScaler and return scaled numpy matrix."""
        X = feature_df[FEATURE_COLUMNS].values
        X_scaled = self.scaler.fit_transform(X)
        self.is_fitted = True
        return X_scaled

    def transform(self, feature_df):
        """Transform feature matrix using fitted scaler."""
        if not self.is_fitted:
            return self.fit_transform(feature_df)
        X = feature_df[FEATURE_COLUMNS].values
        return self.scaler.transform(X)
