from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from logging.handlers import RotatingFileHandler

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for sessions and flash messages

# Setup database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Setup logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Log application startup
app.logger.info('App startup')

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

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    amount = db.Column(db.Float, default=0)

    team = db.relationship('Team', backref=db.backref('deposits', lazy=True))

# Routes
@app.route('/')
def index():
    try:
        teams = Team.query.all()
        challenges = Challenge.query.all()  # Query all challenges
        regions = ['Northern Quarter', 'Ancoats', 'Spinningfields', 'Castlefield', 'Deansgate', 'Piccadilly Gardens', 'Oxford Road']
        
        # Fetch deposit information for each region
        region_deposits = {}
        for region in regions:
            deposits = Deposit.query.filter_by(region=region).all()
            highest_deposit = max(deposits, key=lambda d: d.amount, default=None)
            region_deposits[region] = {
                'total': sum(d.amount for d in deposits),
                'owner': highest_deposit.team.name if highest_deposit else None,
                'team_deposits': {deposit.team.name: deposit.amount for deposit in deposits}
            }

        return render_template('index.html', teams=teams, region_deposits=region_deposits, challenges=challenges)
    except Exception as e:
        app.logger.error(f"Error loading index page: {e}")
        flash(f"Error loading page: {e}")
        return redirect(url_for('index'))

@app.route('/deposit', methods=['POST'])
def deposit():
    try:
        team_id = request.form['team_id']
        region = request.form['region']
        amount = float(request.form['amount'])

        team = Team.query.get(team_id)
        if team.budget < amount:
            flash(f"Not enough budget to deposit £{amount}. Current budget: £{team.budget}.")
            return redirect(url_for('index'))

        # Get existing deposits for this region
        existing_deposits = Deposit.query.filter_by(region=region).all()
        
        # Find the current owner if any
        highest_deposit = max(existing_deposits, key=lambda d: d.amount, default=None)
        current_owner = highest_deposit.team if highest_deposit else None

        # Calculate the new total deposit for the current team
        existing_deposit = Deposit.query.filter_by(team_id=team_id, region=region).first()
        new_total_deposit = (existing_deposit.amount if existing_deposit else 0) + amount

        # If another team owns the region, ensure the new total deposit is enough to win
        if current_owner and current_owner.id != int(team_id) and new_total_deposit <= highest_deposit.amount:
            flash(f"To steal the region, your total deposit must be more than £{highest_deposit.amount}. Your new total would be £{new_total_deposit}.")
            return redirect(url_for('index'))

        # Update or create the deposit for the team
        if existing_deposit:
            existing_deposit.amount += amount
        else:
            new_deposit = Deposit(region=region, team_id=team_id, amount=amount)
            db.session.add(new_deposit)

        # Deduct the amount from the team's budget
        team.budget -= amount
        db.session.commit()

        flash(f"£{amount} deposited in {region}. New total deposit: £{new_total_deposit}. New budget: £{team.budget}.")
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error processing deposit: {e}")
        flash(f"Error processing deposit: {e}")
        return redirect(url_for('index'))

@app.route('/challenges')
def challenges():
    try:
        # Get day and region from query parameters
        day = request.args.get('day')
        region = request.args.get('region')

        # Query challenges based on the day and region
        challenges = Challenge.query.filter_by(day=day, region=region).all()
        if not challenges:
            flash(f"No challenges found for Day {day} in {region}.")
            return redirect(url_for('index'))
        
        return render_template('challenge.html', challenges=challenges, day=day, region=region)
    except Exception as e:
        app.logger.error(f"Error loading challenges for {region} on Day {day}: {e}")
        flash(f"Error loading challenges: {e}")
        return redirect(url_for('index'))


@app.route('/complete_challenge', methods=['POST'])
def complete_challenge():
    try:
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

        db.session.commit()
        flash(f'Challenge completed! New budget: £{team.budget}')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error completing challenge: {e}")
        flash(f"Error completing challenge: {e}")
        return redirect(url_for('index'))

@app.route('/steal_challenge', methods=['POST'])
def steal_challenge():
    try:
        winner_id = request.form['winner_id']
        loser_id = request.form['loser_id']
        percentage = float(request.form['percentage'])

        winner = Team.query.get(winner_id)
        loser = Team.query.get(loser_id)

        steal_amount = loser.budget * (percentage / 100)
        winner.budget += steal_amount
        loser.budget -= steal_amount

        db.session.commit()
        flash(f'Successfully stole {percentage}% of {loser.name}\'s budget! New budget: £{winner.budget}')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error performing steal: {e}")
        flash(f"Error performing steal: {e}")
        return redirect(url_for('index'))

@app.route('/select_transit', methods=['POST'])
def select_transit():
    try:
        team_id = request.form['team_id']
        distance = float(request.form['distance'])
        transport_mode = request.form['transport_mode']

        transport_data = {
            'walking': {'speed': 5, 'cost_per_min': 0},
            'bus': {'speed': 20, 'cost_per_min': 5},  # Half the original cost
            'tram': {'speed': 30, 'cost_per_min': 10},  # Half the original cost
            'train': {'speed': 45, 'cost_per_min': 15},  # Half the original cost
            'taxi': {'speed': 40, 'cost_per_min': 20},  # Half the original cost
            'uber': {'speed': 50, 'cost_per_min': 25}  # Half the original cost
        }

        speed = transport_data[transport_mode]['speed']
        cost_per_min = transport_data[transport_mode]['cost_per_min']

        travel_time = (distance / speed) * 60  # Convert to minutes
        travel_cost = travel_time * cost_per_min

        team = Team.query.get(team_id)
        team.budget -= travel_cost

        db.session.commit()
        flash(f'Travel time: {travel_time:.2f} minutes. Cost: £{travel_cost:.2f}. New budget: £{team.budget:.2f}.')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error selecting transit: {e}")
        flash(f"Error selecting transit: {e}")
        return redirect(url_for('index'))

@app.route('/add_day_bonus')
def add_day_bonus():
    teams = Team.query.all()
    for team in teams:
        team.budget += 1000
    db.session.commit()
    flash('£1000 bonus added to all teams!')
    return redirect(url_for('index'))

@app.route('/admin/reset-teams', methods=['POST'])
def reset_teams():
    try:
        teams = Team.query.all()
        for team in teams:
            team.budget = 2000.0  # Reset budget
        
        # Reset all deposits
        db.session.query(Deposit).delete()
        
        db.session.commit()
        flash('All teams and deposits have been reset.')
    except Exception as e:
        app.logger.error(f"Error resetting teams and deposits: {e}")
        flash(f"Error resetting teams and deposits: {e}")
    return redirect(url_for('index'))

# Ensure database tables are created
with app.app_context():
    db.create_all()  # Create all tables based on models

# Run the app with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
