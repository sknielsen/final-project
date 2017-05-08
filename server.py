from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash,
                   session)
from model import User, Trip, Entry, Category, connect_to_db, db
import os


app = Flask(__name__)

# Required to use Flask sessions
app.secret_key = os.environ['SECRET_KEY']