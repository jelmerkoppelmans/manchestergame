from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for sessions and flash messages

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database and tables are created
    app.run(debug=True)


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

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    amount = db.Column(db.Float, default=0)

    team = db.relationship('Team', backref=db.backref('deposits', lazy=True))

# Routes
@app.route('/')
def index():
    teams = Team.query.all()  # Fetch all teams from the database
    regions = ['Northern Quarter', 'Ancoats', 'Spinningfields', 'Castlefield', 'Deansgate', 'Piccadilly Gardens', 'Oxford Road']
    
    # Fetch deposit information for each region
    region_deposits = {}
    for region in regions:
        deposits = Deposit.query.filter_by(region=region).all()
        highest_deposit = max(deposits, key=lambda d: d.amount, default=None)
        region_deposits[region] = {
            'total': sum(d.amount for d in deposits),
            'owner': highest_deposit.team.name if highest_deposit else None
        }

    return render_template('index.html', teams=teams, region_deposits=region_deposits)

@app.route('/deposit', methods=['POST'])
def deposit():
    team_id = request.form['team_id']
    region = request.form['region']
    amount = float(request.form['amount'])

    team = Team.query.get(team_id)
    if team.budget < amount:
        flash(f"Not enough budget to deposit £{amount}. Current budget: £{team.budget}.")
        return redirect(url_for('index'))

    # Check if the team already has a deposit in the region
    existing_deposit = Deposit.query.filter_by(team_id=team_id, region=region).first()
    
    if existing_deposit:
        # Add to the existing deposit
        existing_deposit.amount += amount
    else:
        # Create a new deposit record
        new_deposit = Deposit(region=region, team_id=team_id, amount=amount)
        db.session.add(new_deposit)

    # Deduct the amount from the team's budget
    team.budget -= amount
    db.session.commit()

    flash(f"£{amount} deposited in {region}. New budget: £{team.budget}.")
    return redirect(url_for('index'))

@app.route('/region_status')
def region_status():
    regions = ['Northern Quarter', 'Ancoats', 'Spinningfields', 'Castlefield', 'Deansgate', 'Piccadilly Gardens', 'Oxford Road']
    
    # Fetch deposit information for each region
    region_deposits = {}
    for region in regions:
        deposits = Deposit.query.filter_by(region=region).all()
        highest_deposit = max(deposits, key=lambda d: d.amount, default=None)
        region_deposits[region] = {
            'total': sum(d.amount for d in deposits),
            'owner': highest_deposit.team.name if highest_deposit else None
        }

    return render_template('region_status.html', region_deposits=region_deposits)

# Create the database tables
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database and tables are created
    app.run(debug=True)
