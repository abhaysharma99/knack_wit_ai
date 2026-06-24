class HiddenGeniusClassifier:

    def classify(self, future_score):

        if future_score >= 80:
            return "High Potential"

        elif future_score >= 50:
            return "Medium Potential"

        else:
            return "Low Potential"