from flask import Blueprint, render_template

combined = Blueprint("combined", __name__)

@combined.route("/combined")
def combined_tab():
    return render_template("combined.html")

