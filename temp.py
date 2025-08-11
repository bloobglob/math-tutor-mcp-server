import random

sections = [("1A", 19), ("1B", 14), ("1C", 13), ("1D", 7), ("1R", 17), ("2A", 10), ("2B", 12), ("2C", 4), ("2R", 16), ("3A", 15), ("3B", 9), ("3C", 20), ("3D", 12), ("3E", 4), ("3F", 6), ("R", 8)]

# Build a list of all odd-numbered questions as (section, question_number)
odd_questions = []
for section, total in sections:
    odd_questions.extend([(section, q) for q in range(1, total + 1, 2)])

# Pick 10 random odd questions
selected = random.sample(odd_questions, 10)
print(sorted(selected))