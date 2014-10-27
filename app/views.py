from flask import render_template, flash, redirect
from app import app
from .forms import LyricsForm
import songtitler

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LyricsForm()
    if form.validate_on_submit():
        inputtext = '{0}'.format(form.lyrics.data)
        processedtext = songtitler.titlepicker(inputtext)
        flash("Some suggested titles for this song:")
        for item in processedtext:
            flash(item)
        return redirect('/')
    return render_template('index.html', form=form)

