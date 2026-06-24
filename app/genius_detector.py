class GeniusDetector:

    def calculate_growth_velocity(self, candidate):
        skills = candidate.get("skills", [])
        return min(len(skills) / 20, 1.0)

    def calculate_learning_consistency(self, candidate):
        certifications = candidate.get("certifications", [])
        return min(len(certifications) / 5, 1.0)

    def calculate_skill_expansion_rate(self, candidate):
        skills = candidate.get("skills", [])
        return min(len(set(skills)) / 15, 1.0)

    def calculate_complexity_growth(self, candidate):
        projects = candidate.get("projects", [])
        return min(len(projects) / 10, 1.0)

    def calculate_certification_trend(self, candidate):
        certs = candidate.get("certifications", [])
        return min(len(certs) / 5, 1.0)

    def calculate_activity_consistency(self, candidate):
        return 0.7

    def generate_growth_signals(self, candidate):
        return {
            "growth_velocity": self.calculate_growth_velocity(candidate),
            "learning_consistency": self.calculate_learning_consistency(candidate),
            "skill_expansion_rate": self.calculate_skill_expansion_rate(candidate),
            "complexity_growth": self.calculate_complexity_growth(candidate),
            "certification_trend": self.calculate_certification_trend(candidate),
            "activity_consistency": self.calculate_activity_consistency(candidate)
        }