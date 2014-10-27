from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired

class LyricsForm(Form):
    lyrics = TextField('lyrics', validators=[DataRequired()])
