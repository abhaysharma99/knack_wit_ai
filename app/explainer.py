class TalentExplainer:

    def generate_reasons(
        self,
        signals,
        future_score,
        potential_level
    ):

        reasons = []

        if signals["growth_velocity"] > 0.5:
            reasons.append(
                "Rapid skill acquisition detected"
            )

        if signals["skill_expansion_rate"] > 0.5:
            reasons.append(
                "Strong skill expansion across domains"
            )

        if signals["complexity_growth"] > 0.5:
            reasons.append(
                "Increasing project complexity observed"
            )

        if signals["learning_consistency"] > 0.5:
            reasons.append(
                "Consistent learning behavior"
            )

        if signals["certification_trend"] > 0.5:
            reasons.append(
                "Strong certification progression"
            )

        if signals["activity_consistency"] > 0.5:
            reasons.append(
                "Good activity consistency"
            )

        if not reasons:
            reasons.append(
                "Candidate is in an early growth stage"
            )

        return {
            "future_score": future_score,
            "potential_level": potential_level,
            "reasons": reasons
        }