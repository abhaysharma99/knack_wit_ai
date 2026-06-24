class FusionEngine:

    def calculate_true_talent_score(
        self,
        current_fit_score,
        future_potential_score
    ):

        score = (
            0.6 * current_fit_score +
            0.4 * future_potential_score
        )

        return round(score, 2)