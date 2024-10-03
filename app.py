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

        challenges = Challenge.query.all()
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

        # Check if the team can steal the region
        if current_owner and current_owner.id != int(team_id) and amount <= highest_deposit.amount:
            flash(f"To steal the region, you must deposit at least £{highest_deposit.amount + 1}.")
            return redirect(url_for('index'))

        # If the team already has a deposit in the region, update it
        existing_deposit = Deposit.query.filter_by(team_id=team_id, region=region).first()
        if existing_deposit:
            existing_deposit.amount += amount
        else:
            new_deposit = Deposit(region=region, team_id=team_id, amount=amount)
            db.session.add(new_deposit)

        team.budget -= amount
        db.session.commit()

        flash(f"£{amount} deposited in {region}. New budget: £{team.budget}.")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error processing deposit: {e}")
        return redirect(url_for('index'))

@app.route('/add_team', methods=['POST'])
def add_team():
    try:
        team_name = request.form['team_name']
        new_team = Team(name=team_name)
        db.session.add(new_team)
        db.session.commit()
        flash(f'Team {team_name} added successfully!')
    except Exception as e:
        flash(f"Error adding team: {e}")
    return redirect(url_for('index'))

@app.route('/complete_challenge', methods=['POST'])
def complete_challenge():
    # Logic for completing a challenge
    pass

@app.route('/steal_challenge', methods=['POST'])
def steal_challenge():
    # Logic for performing a steal
    pass

@app.route('/select_transit', methods=['POST'])
def select_transit():
    # Logic for selecting transit method
    pass

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
        db.session.commit()
        flash('All teams have been reset.')
    except Exception as e:
        flash(f"Error resetting teams: {e}")
    return redirect(url_for('index'))

# Ensure database tables are created
with app.app_context():
    db.create_all()  # Create all tables based on models

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
