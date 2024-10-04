from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# Initialize database
db = SQLAlchemy(app)

# Models
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, default=2000.0)

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    challenge_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.String(20), nullable=False)

# Routes
@app.route('/')
def index():
    teams = Team.query.all()
    challenges = Challenge.query.all()
    # Calculate deposit information for display
    region_deposits = calculate_region_deposits()
    return render_template('index.html', teams=teams, challenges=challenges, region_deposits=region_deposits)

@app.route('/add_team', methods=['POST'])
def add_team():
    team_name = request.form['team_name']
    new_team = Team(name=team_name)
    db.session.add(new_team)
    db.session.commit()
    flash(f'Team "{team_name}" added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/complete_challenge', methods=['POST'])
def complete_challenge():
    team_id = request.form['team_id']
    challenge_id = request.form['challenge_id']
    wager = float(request.form['wager'])
    result = request.form['result']

    team = Team.query.get(team_id)
    challenge = Challenge.query.get(challenge_id)

    # Determine multiplier based on challenge level
    multiplier = 1.5 if challenge.level == 'Easy' else 2 if challenge.level == 'Moderate' else 3

    challenge_won = False
    if result == 'win':
        team.budget += wager * multiplier
        challenge_won = True
        flash(f'Challenge won! Budget increased by £{wager * multiplier}.', 'success')
    else:
        team.budget -= wager
        flash(f'Challenge lost! Budget decreased by £{wager}.', 'danger')

    db.session.commit()

    # Redirect to index with challenge_won flag
    return redirect(url_for('index', challenge_won=challenge_won))

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
    flash(f'{percentage}% of {loser.name}\'s budget stolen! New budget: £{winner.budget}', 'success')
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
    flash(f'Travel time: {travel_time:.2f} minutes. Cost: £{travel_cost:.2f}. New budget: £{team.budget:.2f}.', 'success')
    return redirect(url_for('index'))

@app.route('/add_day_bonus')
def add_day_bonus():
    teams = Team.query.all()
    for team in teams:
        team.budget += 1000
    db.session.commit()
    flash('£1000 bonus added to all teams!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/reset_teams', methods=['POST'])
def reset_teams():
    try:
        # Reset team budgets and delete all deposits
        teams = Team.query.all()
        for team in teams:
            team.budget = 2000.0  # Reset team budget to the initial value

        # Delete all deposits
        Deposit.query.delete()

        db.session.commit()
        flash('All teams and deposits have been reset successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting teams: {str(e)}', 'danger')

    return redirect(url_for('index'))

# Helper function to calculate region deposits and owners
def calculate_region_deposits():
    regions = db.session.query(Deposit.region).distinct().all()
    region_deposits = {}

    for region in regions:
        deposits = Deposit.query.filter_by(region=region[0]).all()
        total_deposit = sum(deposit.amount for deposit in deposits)
        team_deposits = {}
        for deposit in deposits:
            team = Team.query.get(deposit.team_id)
            if team.name in team_deposits:
                team_deposits[team.name] += deposit.amount
            else:
                team_deposits[team.name] = deposit.amount

        # Determine the current owner (team with the largest deposit)
        owner = max(team_deposits, key=team_deposits.get) if team_deposits else None

        # Store the deposit data for the region
        region_deposits[region[0]] = {
            'total': total_deposit,
            'owner': owner,
            'team_deposits': team_deposits
        }

    return region_deposits

# Initialize database tables
@app.before_first_request
def create_tables():
    db.create_all()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
