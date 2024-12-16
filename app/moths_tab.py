from flask import Blueprint, render_template

moths = Blueprint("moths", __name__)

@moths.route("/moths")
def moths_tab():
    return render_template("moths.html")
