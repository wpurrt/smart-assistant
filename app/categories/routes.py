from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user


from app.categories import categories_bp
from app.extensions import db
from app.forms import CategoryForm
from app.models import Category


@categories_bp.route("/", methods=["GET", "POST"])
@login_required
def list_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        existing = Category.query.filter_by(
            user_id=current_user.id,
            name=form.name.data.strip()
        ).first()
        if existing:
            flash("Такая категория уже существует.", "danger")
            return redirect(url_for("categories.list_categories"))
        category = Category(
            name=form.name.data.strip(),
            color=form.color.data.strip() or "#3498db",
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        flash("Категория успешно добавлена.", "success")
        return redirect(url_for("categories.list_categories"))
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.created_at.desc()).all()
    return render_template("categories/list.html", form=form, categories=categories)


@categories_bp.route("/delete/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    flash("Категория удалена.", "info")
    return redirect(url_for("categories.list_categories"))