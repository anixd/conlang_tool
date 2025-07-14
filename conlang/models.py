from conlang import db

class Word(db.Model):
    __tablename__ = "words"
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(), nullable=False)
    transcription = db.Column(db.String(), nullable=False)
    translation_1 = db.Column(db.String)
    translation_2 = db.Column(db.String)
    root = db.Column(db.String(100))
    comment = db.Column(db.Text)
    etymologies = db.relationship('Etymology', backref='word', lazy=True)


class Etymology(db.Model):
    __tablename__ = "etymologies"
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text)
