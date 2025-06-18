import numpy as np
class PassiveAggressiveClassifier:
    def __init__(self, max_iter=100, C=1.0, mode="PA-I"):
        self.max_iter = max_iter
        self.C = C
        self.mode = mode

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features)

        for epoch in range(self.max_iter):
            for i in range(n_samples):
                x_i = X[i]
                y_i = y[i] * 2 - 1

                loss = max(0, 1 - y_i * np.dot(self.w, x_i))

                if loss > 0:
                    if self.mode == "PA-I":
                        tau = loss / (np.linalg.norm(x_i) ** 2 + 1e-10)
                    else:
                        raise ValueError("Invalid mode. Use 'PA-I'.")

                    self.w += tau * y_i * x_i

    def predict(self, X):
        return np.where(np.dot(X, self.w) >= 0, 1, 0)

    def score(self, X, y):
        preds = self.predict(X)
        return np.mean(preds == y)