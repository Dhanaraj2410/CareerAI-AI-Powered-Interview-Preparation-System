import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'careerai.settings')
django.setup()

from aptitude.models import Question

def seed_aptitude_questions():
    questions_data = [
        # Quantitative
        {
            "category": "quantitative",
            "difficulty": "easy",
            "topic": "Percentage",
            "question": "What is 20% of 450?",
            "option_a": "80", "option_b": "90", "option_c": "95", "option_d": "100",
            "correct_answer": "B",
            "formula": "Percentage = (Rate / 100) * Base Value",
            "solution_steps": "1. Rate = 20%\n2. Calculation: (20 / 100) * 450 = 0.20 * 450 = 90.\n3. Therefore, 20% of 450 is 90.",
            "explanation": "To calculate a percentage, multiply the percentage rate by the total value and divide by 100."
        },
        {
            "category": "quantitative",
            "difficulty": "easy",
            "topic": "Basic Arithmetic & Speed",
            "question": "If a car travels at 60 km/h, how far will it travel in 2.5 hours?",
            "option_a": "120 km", "option_b": "140 km", "option_c": "150 km", "option_d": "180 km",
            "correct_answer": "C",
            "formula": "Distance = Speed * Time",
            "solution_steps": "1. Given Speed = 60 km/h and Time = 2.5 hours.\n2. Calculation: Distance = 60 * 2.5 = 150 km.\n3. Therefore, the car covers 150 km.",
            "explanation": "Distance traveled equals speed multiplied by time."
        },
        {
            "category": "quantitative",
            "difficulty": "medium",
            "topic": "Profit & Loss",
            "question": "An article is bought for $400 and sold for $500. What is the profit percentage?",
            "option_a": "20%", "option_b": "25%", "option_c": "30%", "option_d": "15%",
            "correct_answer": "B",
            "formula": "Profit % = ((Selling Price - Cost Price) / Cost Price) * 100",
            "solution_steps": "1. Profit = Selling Price ($500) - Cost Price ($400) = $100.\n2. Profit % = ($100 / $400) * 100 = 0.25 * 100 = 25%.\n3. Therefore, profit percentage is 25%.",
            "explanation": "Profit percentage measures profit gained relative to initial cost price."
        },
        {
            "category": "quantitative",
            "difficulty": "medium",
            "topic": "Time & Work",
            "question": "A can complete a job in 10 days and B in 15 days. How long will they take working together?",
            "option_a": "5 days", "option_b": "6 days", "option_c": "7.5 days", "option_d": "8 days",
            "correct_answer": "B",
            "formula": "Combined Time = (A * B) / (A + B)",
            "solution_steps": "1. A's 1-day work = 1/10; B's 1-day work = 1/15.\n2. Combined 1-day work = (1/10) + (1/15) = (3 + 2) / 30 = 5/30 = 1/6.\n3. Total time taken = 6 days.",
            "explanation": "Add individual daily work rates to calculate total combined completion time."
        },
        {
            "category": "quantitative",
            "difficulty": "hard",
            "topic": "Probability",
            "question": "What is the probability of getting a total sum of 7 when rolling two fair 6-sided dice?",
            "option_a": "1/6", "option_b": "1/12", "option_c": "5/36", "option_d": "1/36",
            "correct_answer": "A",
            "formula": "Probability = Favorable Outcomes / Total Outcomes",
            "solution_steps": "1. Total outcomes = 6 * 6 = 36.\n2. Pairs giving sum 7: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) -> 6 outcomes.\n3. Probability = 6 / 36 = 1/6.",
            "explanation": "Identify total possible dice combinations (36) and count combinations summing to 7 (6 combinations)."
        },

        # Logical Reasoning
        {
            "category": "reasoning",
            "difficulty": "easy",
            "topic": "Series Completion",
            "question": "Complete the sequence: 2, 4, 8, 16, 32, __",
            "option_a": "48", "option_b": "64", "option_c": "50", "option_d": "128",
            "correct_answer": "B",
            "formula": "Term_n = Term_(n-1) * 2",
            "solution_steps": "1. Pattern: Each term doubles the previous number.\n2. 32 * 2 = 64.\n3. Next number in series is 64.",
            "explanation": "Geometric progression doubling each term."
        },
        {
            "category": "reasoning",
            "difficulty": "medium",
            "topic": "Blood Relations",
            "question": "Pointing to a photograph, John said, 'His mother is the only daughter of my mother.' How is John related to the person in the photograph?",
            "option_a": "Brother", "option_b": "Uncle", "option_c": "Father", "option_d": "Grandfather",
            "correct_answer": "B",
            "formula": "Logic Mapping",
            "solution_steps": "1. 'Only daughter of my mother' = John's sister.\n2. 'His mother' = John's sister.\n3. John is the brother of the person's mother, making John his Uncle.",
            "explanation": "Deconstruct relation statements step-by-step from the speaker's perspective."
        },
        {
            "category": "reasoning",
            "difficulty": "medium",
            "topic": "Direction Sense",
            "question": "A person walks 5 km North, turns right and walks 3 km, then turns right again and walks 5 km. How far is he from his starting point?",
            "option_a": "3 km", "option_b": "5 km", "option_c": "8 km", "option_d": "13 km",
            "correct_answer": "A",
            "formula": "Displacement = Net East/West Shift",
            "solution_steps": "1. Walk 5 km North (+5 Y).\n2. Turn right 3 km East (+3 X).\n3. Turn right 5 km South (-5 Y).\n4. Final position: 3 km East of origin. Distance = 3 km.",
            "explanation": "North and South movements cancel each other out, leaving only the Eastward displacement."
        },

        # Verbal Ability
        {
            "category": "verbal",
            "difficulty": "easy",
            "topic": "Synonyms",
            "question": "Select the synonym of 'CANDID':",
            "option_a": "Secretive", "option_b": "Frank", "option_c": "Dishonest", "option_d": "Vague",
            "correct_answer": "B",
            "formula": "Vocabulary Definition",
            "solution_steps": "1. 'Candid' means truthful, straightforward, and frank.\n2. 'Frank' is the closest synonym.",
            "explanation": "Candid means open and sincere in expression."
        },
        {
            "category": "verbal",
            "difficulty": "medium",
            "topic": "Antonyms",
            "question": "Select the antonym of 'METICULOUS':",
            "option_a": "Careful", "option_b": "Careless", "option_c": "Detailed", "option_d": "Precise",
            "correct_answer": "B",
            "formula": "Vocabulary Definition",
            "solution_steps": "1. 'Meticulous' means showing great attention to detail.\n2. The opposite (antonym) is 'Careless'.",
            "explanation": "Meticulous implies thoroughness and extreme care."
        },

        # Data Interpretation
        {
            "category": "data_interpretation",
            "difficulty": "medium",
            "topic": "Bar Chart",
            "question": "Company revenue grew from $120M in 2024 to $150M in 2025. What is the percentage increase?",
            "option_a": "20%", "option_b": "25%", "option_c": "30%", "option_d": "15%",
            "correct_answer": "B",
            "formula": "Percentage Increase = ((New Value - Old Value) / Old Value) * 100",
            "solution_steps": "1. Increase = $150M - $120M = $30M.\n2. Percentage Increase = ($30M / $120M) * 100 = 0.25 * 100 = 25%.",
            "explanation": "Calculate change in value divided by original baseline value."
        }
    ]

    for item in questions_data:
        Question.objects.get_or_create(
            question=item["question"],
            defaults=item
        )

    print(f"Successfully seeded {len(questions_data)} aptitude questions with solution steps and formulas!")

if __name__ == '__main__':
    seed_aptitude_questions()
