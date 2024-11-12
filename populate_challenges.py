import os
import pandas as pd
from app import db, Challenge, app

# Define the path for the CSV file in the same directory
file_path = os.path.join(os.path.dirname(__file__), 'challenges.csv')
challenges_df = pd.read_csv(file_path)

# Function to clear and seed the challenges
def populate_challenges():
    db.session.query(Challenge).delete()  # Clear existing challenges

    for _, row in challenges_df.iterrows():
        # Determine steal percentage
        if row['steal'].strip().lower() == 'yes':
            if row['level'] == 'Easy':
                steal_percentage = 30
            elif row['level'] == 'Moderate':
                steal_percentage = 40
            elif row['level'] == 'Hard':
                steal_percentage = 50
        else:
            steal_percentage = 0  # Non-steal challenges

        # Create a new Challenge entry
        new_challenge = Challenge(
            region=row['region'],
            day=row['day'],
            challenge_name=row['challenge_name'],
            description=row['description'],
            level=row['level'],
            steal_percentage=steal_percentage
        )
        db.session.add(new_challenge)

    db.session.commit()  # Commit changes to the database

# Run the seeding function
if __name__ == '__main__':
    with app.app_context():
        populate_challenges()
    print('Challenges successfully populated!')
