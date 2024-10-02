from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for sessions and flash messages

# Setup database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Models
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, default=2000.0)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    challenge_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.String(20), nullable=False)

class RegionBonus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

# Routes
@app.route('/')
def index():
    teams = Team.query.all()  # Fetch all teams from the database
    challenges = Challenge.query.all()  # Fetch all challenges from the database
    return render_template('index.html', teams=teams, challenges=challenges)

@app.route('/add_team', methods=['POST'])
def add_team():
    team_name = request.form['team_name']
    new_team = Team(name=team_name)
    db.session.add(new_team)
    db.session.commit()
    flash('Team added successfully!')
    return redirect(url_for('index'))

@app.route('/challenges/<int:day>/<string:region>')
def challenges(day, region):
    challenges = Challenge.query.filter_by(day=day, region=region).all()
    return render_template('challenge.html', challenges=challenges, day=day, region=region)

@app.route('/complete_challenge', methods=['POST'])
def complete_challenge():
    team_id = request.form['team_id']
    challenge_id = request.form['challenge_id']
    wager = float(request.form['wager'])
    result = request.form['result']
    
    team = Team.query.get(team_id)
    challenge = Challenge.query.get(challenge_id)
    
    multiplier = 1.5 if challenge.level == 'Easy' else 2 if challenge.level == 'Moderate' else 3
    
    if result == 'win':
        team.budget += wager * multiplier
    else:
        team.budget -= wager
    
    # Check for region bonus
    if not RegionBonus.query.filter_by(region=challenge.region).first():
        team.budget += 500
        new_bonus = RegionBonus(region=challenge.region, team_id=team.id)
        db.session.add(new_bonus)
    
    db.session.commit()
    flash(f'Challenge completed! New budget: £{team.budget}')
    return redirect(url_for('index'))

@app.route('/steal_challenge', methods=['POST'])
def steal_challenge():
    winner_id = request.form['winner_id']
    loser_id = request.form['loser_id']
    percentage = float(request.form['percentage'])
    
    winner = Team.query.get(winner_id)
    loser = Team.query.get(loser_id)
    
    steal_amount = loser.budget * (percentage / 100)
    winner.budget += steal_amount
    loser.budget -= steal_amount
    
    db.session.commit()
    flash(f'{percentage}% of {loser.name}\'s budget stolen! New budget: £{winner.budget}')
    return redirect(url_for('index'))

@app.route('/select_transit', methods=['POST'])
def select_transit():
    team_id = request.form['team_id']
    distance = float(request.form['distance'])  # Distance in kilometers
    transport_mode = request.form['transport_mode']
    
    # Define speeds and costs per mode of transport
    transport_data = {
        'walking': {'speed': 5, 'cost_per_min': 0},
        'bus': {'speed': 20, 'cost_per_min': 10},
        'tram': {'speed': 30, 'cost_per_min': 20},
        'train': {'speed': 45, 'cost_per_min': 30},
        'taxi': {'speed': 40, 'cost_per_min': 40},
        'uber': {'speed': 50, 'cost_per_min': 50}
    }
    
    # Get the speed and cost per minute for the selected transport mode
    speed = transport_data[transport_mode]['speed']  # km/h
    cost_per_min = transport_data[transport_mode]['cost_per_min']  # £/min
    
    # Calculate the time it takes to travel the distance (in minutes)
    travel_time = (distance / speed) * 60  # Convert to minutes
    
    # Calculate the total cost of the travel
    travel_cost = travel_time * cost_per_min
    
    # Deduct the travel cost from the team's budget
    team = Team.query.get(team_id)
    team.budget -= travel_cost
    db.session.commit()
    
    # Flash a message showing the travel time and cost
    flash(f'Travel time: {travel_time:.2f} minutes. Cost: £{travel_cost:.2f}. New budget: £{team.budget:.2f}.')
    return redirect(url_for('index'))

@app.route('/add_day_bonus')
def add_day_bonus():
    teams = Team.query.all()
    for team in teams:
        team.budget += 1000
    db.session.commit()
    flash('£1000 bonus added to all teams!')
    return redirect(url_for('index'))

# Create the database tables
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database and tables are created
    app.run(debug=True)
