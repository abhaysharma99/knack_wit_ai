from genius_detector import GeniusDetector
from future_potential import FuturePotentialScorer
from classifier import HiddenGeniusClassifier
from fusion_engine import FusionEngine
from explainer import TalentExplainer

candidate = {
    "skills": [
        "Python",
        "Machine Learning",
        "FastAPI",
        "Docker"
    ],
    "projects": [
        "Chatbot",
        "Recommendation System"
    ],
    "certifications": [
        "AWS"
    ]
}

# Step 1: Growth Signals
detector = GeniusDetector()
signals = detector.generate_growth_signals(candidate)

# Step 2: Future Potential Score
scorer = FuturePotentialScorer()
future_score = scorer.calculate_score(signals)

# Step 3: Hidden Genius Classification
classifier = HiddenGeniusClassifier()
potential_level = classifier.classify(future_score)

# Step 4: Fusion Engine
current_fit_score = 75

fusion_engine = FusionEngine()

true_talent_score = fusion_engine.calculate_true_talent_score(
    current_fit_score,
    future_score
)

# Step 5: Explainability Layer
explainer = TalentExplainer()

analysis = explainer.generate_reasons(
    signals,
    future_score,
    potential_level
)

# Output
print("\n=== Growth Signals ===")
print(signals)

print("\n=== Future Potential Analysis ===")
print("Future Potential Score:", future_score)
print("Potential Level:", potential_level)

print("\n=== Fusion Engine ===")
print("Current Fit Score:", current_fit_score)
print("True Talent Score:", true_talent_score)

print("\n=== Explainability Layer ===")
print(analysis)