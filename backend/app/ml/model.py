import os
import joblib
from abc import ABC, abstractmethod
from sklearn.ensemble import IsolationForest

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'datasets')
MODEL_PATH = os.path.join(MODEL_DIR, 'pretrained_model.joblib')

class BaseAnomalyModel(ABC):
    @abstractmethod
    def train(self, X_scaled):
        pass

    @abstractmethod
    def predict_anomaly_scores(self, X_scaled):
        pass

class IsolationForestModel(BaseAnomalyModel):
    def __init__(self, contamination=0.1, n_estimators=100, random_state=42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state
        )
        self.is_trained = False

    def train(self, X_scaled):
        if len(X_scaled) == 0:
            return
        self.model.fit(X_scaled)
        self.is_trained = True

    def predict_anomaly_scores(self, X_scaled):
        """
        Returns raw decision scores.
        Isolation Forest score_samples yields values where negative numbers indicate anomalies.
        """
        if not self.is_trained:
            self.train(X_scaled)

        # score_samples returns opposite of anomaly score; lower values mean more anomalous
        scores = self.model.score_samples(X_scaled)
        return scores

    def save_model(self, path=MODEL_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)

    def load_model(self, path=MODEL_PATH):
        if os.path.exists(path):
            self.model = joblib.load(path)
            self.is_trained = True
            return True
        return False
