from flask import Blueprint, render_template, request, redirect, url_for, Response
from conlang import db
from conlang.models import Word, Etymology
from conlang.forms import WordForm, EtymologyForm
from sqlalchemy import text, or_
from conlang.utils import render_markdown
from urllib.parse import quote

main = Blueprint('main', __name__)


@main.route('/')
def index():
    words = Word.query.order_by(Word.word).all()
    return render_template('index.html', words=words, render_markdown=render_markdown)


@main.route('/word/add', methods=['GET', 'POST'])
def add_word():
    form = WordForm()
    if form.validate_on_submit():
        word = Word(
            word=form.word.data,
            transcription=form.transcription.data,
            translation_1=form.translation_1.data,
            translation_2=form.translation_2.data,
            root=form.root.data,
            description=form.description.data,
            comment=form.comment.data
        )
        db.session.add(word)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('word_form.html', form=form, title='Добавить слово')


@main.route('/word/edit/<int:id>', methods=['GET', 'POST'])
def edit_word(id):
    word = Word.query.get_or_404(id)
    form = WordForm(obj=word)
    if form.validate_on_submit():
        word.word = form.word.data
        word.transcription = form.transcription.data
        word.translation_1 = form.translation_1.data
        word.translation_2 = form.translation_2.data
        word.root = form.root.data
        word.description = form.description.data
        word.comment = form.comment.data
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('word_form.html', form=form, title='Редактировать слово')


@main.route('/word/delete/<int:id>', methods=['POST'])
def delete_word(id):
    word = Word.query.get_or_404(id)
    db.session.delete(word)
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/word/<int:id>/etymology/add', methods=['GET', 'POST'])
def add_etymology(id):
    word = Word.query.get_or_404(id)
    form = EtymologyForm()
    if form.validate_on_submit():
        etymology = Etymology(
            word_id=word.id,
            explanation=form.explanation.data,
            comment=form.comment.data
        )
        db.session.add(etymology)
        db.session.commit()
        return redirect(url_for('main.view_word', id=word.id))
    return render_template('etymology_form.html', form=form, word=word, title='Добавить этимологию')


@main.route('/word/<int:id>')
def view_word(id):
    word = Word.query.get_or_404(id)
    return render_template('word_detail.html', word=word, render_markdown=render_markdown)


@main.route('/search')
def search():
    query = request.args.get('q', '')
    db_type = os.getenv('DB_TYPE', 'sqlite')

    if query:
        if db_type == 'postgresql':
            search_query = text("""
                SELECT words.* 
                FROM words 
                WHERE to_tsvector('simple', word || ' ' || 
                                coalesce(transcription, '') || ' ' || 
                                coalesce(translation_1, '') || ' ' || 
                                coalesce(translation_2, '') || ' ' || 
                                coalesce(root, '') || ' ' || 
                                coalesce(description, '') || ' ' || 
                                coalesce(comment, '')) @@ to_tsquery('simple', :query || ':*')
                UNION
                SELECT words.*
                FROM words
                JOIN etymologies ON words.id = etymologies.word_id
                WHERE to_tsvector('simple', etymologies.explanation || ' ' || 
                                coalesce(etymologies.comment, '')) @@ to_tsquery('simple', :query || ':*')
            """)
            words = db.session.execute(search_query, {'query': query}).fetchall()
        else:  # SQLite
            search_pattern = f'%{query}%'
            words = Word.query.join(Etymology, isouter=True).filter(
                or_(
                    Word.word.ilike(search_pattern),
                    Word.transcription.ilike(search_pattern),
                    Word.translation_1.ilike(search_pattern),
                    Word.translation_2.ilike(search_pattern),
                    Word.root.ilike(search_pattern),
                    Word.description.ilike(search_pattern),
                    Word.comment.ilike(search_pattern),
                    Etymology.explanation.ilike(search_pattern),
                    Etymology.comment.ilike(search_pattern)
                )
            ).distinct().order_by(Word.word).all()
    else:
        words = Word.query.order_by(Word.word).all()
    return render_template('index.html', words=words, query=query, render_markdown=render_markdown)


@main.route('/export')
def export_markdown():
    words = Word.query.order_by(Word.word).all()
    output = "# Словарь языка anik'e\n\n"

    for word in words:
        output += f"## {word.word}\n"
        output += f"- **Транскрипция**: {word.transcription or 'N/A'}\n"
        output += f"- **Описание**: {word.description or 'N/A'}\n"
        output += f"- **Перевод 1**: {word.translation_1 or 'N/A'}\n"
        output += f"- **Перевод 2**: {word.translation_2 or 'N/A'}\n"
        output += f"- **Корень**: {word.root or 'N/A'}\n"
        if word.comment:
            output += f"- **Комментарий**:\n{word.comment}\n"

        if word.etymologies:
            output += "\n<details>\n<summary>Этимология</summary>\n\n"
            for etymology in word.etymologies:
                output += f"- **Объяснение**:\n{etymology.explanation}\n"
                if etymology.comment:
                    output += f"- **Комментарий**:\n{etymology.comment}\n"
                output += "\n"
            output += "</details>\n"

        output += "\n"
        output += "\n---\n\n"

    return Response(
        output,
        mimetype='text/markdown',
        headers={'Content-Disposition': 'attachment;filename=dictionary.md'}
    )


@main.route('/word/<int:id>/export')
def export_single_word(id):
    word = Word.query.get_or_404(id)
    output = f"# {word.word}\n"
    output += f"- **Транскрипция**: {word.transcription or 'N/A'}\n"
    output += f"- **Описание**: {word.description or 'N/A'}\n"
    output += f"- **Перевод 1**: {word.translation_1 or 'N/A'}\n"
    output += f"- **Перевод 2**: {word.translation_2 or 'N/A'}\n"
    output += f"- **Корень**: {word.root or 'N/A'}\n"

    if word.comment:
        output += f"- **Комментарий**:\n{word.comment}\n"

    if word.etymologies:
        output += "\n<details>\n<summary>Этимология</summary>\n\n"
        for etymology in word.etymologies:
            output += f"- **Объяснение**:\n{etymology.explanation}\n"
            if etymology.comment:
                output += f"- **Комментарий**:\n{etymology.comment}\n"
            output += "\n"
        output += "</details>\n"

    output += "\n"
    output += "\n---\n\n"

    filename = f"{word.word}.md"
    ascii_filename = quote(filename.encode("utf-8"))

    return Response(
        output,
        mimetype='text/markdown',
        headers={
            'Content-Disposition': f"attachment; filename*=UTF-8''{ascii_filename}"
        }
    )
