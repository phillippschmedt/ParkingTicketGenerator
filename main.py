import os

from flask import Flask, render_template, request, send_file
from flask_wtf import FlaskForm
from wtforms import DateField, StringField
from wtforms.validators import DataRequired

import ticket_generator

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

class TicketForm(FlaskForm):
    plate = StringField('plate', validators=[DataRequired(message="Ungültiges Kennzeichen")])
    date = DateField('date', format='%d.%m.%Y', validators=[DataRequired(message="Ungültiges Datum")])

@app.route('/', methods=["GET", "POST"])
def create_ticket_endpoint():
    form = TicketForm()
    if form.validate_on_submit():
        return send_file(ticket_generator.create_ticket(form.date.data, form.plate.data), attachment_filename='ticket.pdf')
    return render_template("index.html", form=form)
