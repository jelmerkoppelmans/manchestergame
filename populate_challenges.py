from app import db, Challenge, app  # Import app from app.py

# Function to clear and seed the challenges
def populate_challenges():
    # Clear existing challenges
    db.session.query(Challenge).delete()
    
    # List of challenges to be added
    challenges = [
        # Day 1 - Northern Quarter
        {
            'region': 'Northern Quarter',
            'day': 1,
            'challenge_name': 'Atom Split Surprise',
            'description': 'Create a science demo to simulate the splitting of the atom.',
            'level': 'Moderate'
        },
        {
            'region': 'Northern Quarter',
            'day': 1,
            'challenge_name': 'Straw Tower Power',
            'description': 'Build a 50 cm tall straw tower that can stand for 10 seconds using only materials found around you.',
            'level': 'Easy'
        },
        {
            'region': 'Northern Quarter',
            'day': 1,
            'challenge_name': 'Make a Putt',
            'description': 'Roll a ball into a 6-inch cup from 10 feet. Set up items to guide the ball.',
            'level': 'Moderate'
        },
        {
            'region': 'Northern Quarter',
            'day': 1,
            'challenge_name': 'Vinyl Guesswork',
            'description': 'Recreate a famous album cover pose while one team member guesses the album.',
            'level': 'Moderate'
        },
        # Day 1 - Ancoats
        {
            'region': 'Ancoats',
            'day': 1,
            'challenge_name': 'Roll that Cheese',
            'description': 'Roll a ball of cheese in a straight line for 15 meters.',
            'level': 'Easy'
        },
        {
            'region': 'Ancoats',
            'day': 1,
            'challenge_name': 'Cake through a Straw',
            'description': 'Consume at least 1/3 of a slice of cake using a straw. The cake may be in any form.',
            'level': 'Moderate'
        },
        {
            'region': 'Ancoats',
            'day': 1,
            'challenge_name': 'Catch the Dog',
            'description': 'Throw a sausage into a bun from 10 meters away. The catcher cannot use their hands.',
            'level': 'Moderate'
        },
        {
            'region': 'Ancoats',
            'day': 1,
            'challenge_name': 'Egg Survival Drop',
            'description': 'Build a vessel for an egg, throw it 10 feet in the air, and it must survive without cracking.',
            'level': 'Moderate'
        },
        # Day 2 - Spinningfields
        {
            'region': 'Spinningfields',
            'day': 2,
            'challenge_name': 'Buzzing Riddle',
            'description': 'Solve a bee-related riddle under a bridge. You have one guess to get it right.',
            'level': 'Moderate'
        },
        {
            'region': 'Spinningfields',
            'day': 2,
            'challenge_name': 'Egg Drop Defense',
            'description': 'Create a vessel for an egg, throw it 10 feet into the air, and it must survive without cracking.',
            'level': 'Moderate'
        },
        {
            'region': 'Spinningfields',
            'day': 2,
            'challenge_name': 'Dutch Dare',
            'description': 'Commit an act that is legal in the UK but illegal in the Netherlands.',
            'level': 'Easy'
        },
        {
            'region': 'Spinningfields',
            'day': 2,
            'challenge_name': 'Find the Town Hall',
            'description': 'Find the local town hall without using your phone or asking for help. You have 30 minutes.',
            'level': 'Hard'
        },
        # Day 2 - Castlefield
        {
            'region': 'Castlefield',
            'day': 2,
            'challenge_name': 'Use a Fancy Restroom',
            'description': 'Use the restroom of a hotel where the room costs more than $500 a night.',
            'level': 'Moderate'
        },
        {
            'region': 'Castlefield',
            'day': 2,
            'challenge_name': 'Build and Ride a Go-Kart',
            'description': 'Build a go-kart with at least 4 wheels and ride it 50 meters down a hill.',
            'level': 'Hard'
        },
        {
            'region': 'Castlefield',
            'day': 2,
            'challenge_name': 'Give a Piggyback Ride',
            'description': 'Carry your teammate around the perimeter of a local park. You can switch off at any time.',
            'level': 'Moderate'
        },
        {
            'region': 'Castlefield',
            'day': 2,
            'challenge_name': 'Touch a Bird',
            'description': 'Find and touch a live bird with your hands.',
            'level': 'Moderate'
        },
        # Day 2 - Deansgate
        {
            'region': 'Deansgate',
            'day': 2,
            'challenge_name': 'Water Transfer Hunt',
            'description': 'Transfer a cup of water from one fountain to another without spilling more than 1/4 of it.',
            'level': 'Moderate'
        },
        {
            'region': 'Deansgate',
            'day': 2,
            'challenge_name': 'Egg Eater',
            'description': 'Eat an egg in any form, but it must clearly be recognizably an egg.',
            'level': 'Moderate'
        },
        {
            'region': 'Deansgate',
            'day': 2,
            'challenge_name': 'Pop Goes the Kernel',
            'description': 'Pop a single kernel of corn using any method.',
            'level': 'Moderate'
        },
        # Day 2 - Piccadilly Gardens
        {
            'region': 'Piccadilly Gardens',
            'day': 2,
            'challenge_name': 'Beer Pong Bounce',
            'description': 'Throw a ball into a cup filled with beer from a distance of 6 feet. You get 5 attempts.',
            'level': 'Moderate'
        },
        {
            'region': 'Piccadilly Gardens',
            'day': 2,
            'challenge_name': 'Bee Tracker',
            'description': 'Record a bee on camera continuously for 30 seconds without losing sight of it.',
            'level': 'Hard'
        },
        {
            'region': 'Piccadilly Gardens',
            'day': 2,
            'challenge_name': 'Make A Recognizable Portrait',
            'description': 'Create a recognizable portrait of a person from a local museum and have your teammates guess it.',
            'level': 'Moderate'
        },
        {
            'region': 'Piccadilly Gardens',
            'day': 2,
            'challenge_name': 'Painted Pedicure',
            'description': 'Both team members must get a pedicure with their nails painted in state colors.',
            'level': 'Hard'
        }
    ]
    
    # Add each challenge to the database
    for challenge in challenges:
        new_challenge = Challenge(
            region=challenge['region'],
            day=challenge['day'],
            challenge_name=challenge['challenge_name'],
            description=challenge['description'],
            level=challenge['level']
        )
        db.session.add(new_challenge)
    
    # Commit the changes to the database
    db.session.commit()

# Run the seeding function
if __name__ == '__main__':
    with app.app_context():  # Use the app's context for database access
        populate_challenges()
    print('Challenges successfully populated!')
