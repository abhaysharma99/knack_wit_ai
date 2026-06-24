class FuturePotentialScorer:

    def calculate_score(self, signals):

        score = (
            0.25 * signals["growth_velocity"] +
            0.15 * signals["learning_consistency"] +
            0.20 * signals["skill_expansion_rate"] +
            0.25 * signals["complexity_growth"] +
            0.05 * signals["certification_trend"] +
            0.10 * signals["activity_consistency"]
        )

        return round(score * 100, 2)
