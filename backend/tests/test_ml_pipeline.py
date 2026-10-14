import pytest
from app import create_app
from app.utils.db import get_db
from app.ml.synthetic_generator import generate_synthetic_dataset
from app.ml.preprocessor import FeaturePreprocessor
from app.ml.model import IsolationForestModel

@pytest.fixture
def app_db():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db = get_db()
        yield db

def test_synthetic_generator_and_preprocessor(app_db):
    res = generate_synthetic_dataset(num_days=2, reset_db=True)
    assert res['users_created'] == 14
    assert res['activities_created'] > 0

    activities = list(app_db.activities.find({}, {'_id': 0}))
    users = {u['user_id']: u for u in app_db.users.find({}, {'_id': 0})}

    preprocessor = FeaturePreprocessor()
    feat_df = preprocessor.extract_features_from_activities(activities, users)
    assert len(feat_df) == 14

    X_scaled = preprocessor.fit_transform(feat_df)
    assert X_scaled.shape == (14, 7)

def test_isolation_forest_model(app_db):
    activities = list(app_db.activities.find({}, {'_id': 0}))
    users = {u['user_id']: u for u in app_db.users.find({}, {'_id': 0})}

    preprocessor = FeaturePreprocessor()
    feat_df = preprocessor.extract_features_from_activities(activities, users)
    X_scaled = preprocessor.fit_transform(feat_df)

    model = IsolationForestModel(contamination=0.1)
    model.train(X_scaled)
    scores = model.predict_anomaly_scores(X_scaled)

    assert len(scores) == 14
    model.save_model()
