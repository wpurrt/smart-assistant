from datetime import datetime
from app.models import Task, Category


def get_dashboard_stats(user):
    now = datetime.utcnow()

    tasks = Task.query.filter_by(user_id=user.id).all()
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.is_done])
    active_tasks = len([t for t in tasks if not t.is_done])
    overdue_tasks = len([t for t in tasks if not t.is_done and t.deadline and t.deadline < now])
    nearest_task = Task.query.filter(
        Task.user_id == user.id,
        Task.is_done.is_(False),
        Task.deadline.isnot(None)
    ).order_by(Task.deadline.asc()).first()
    completion_rate = round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "active_tasks": active_tasks,
        "overdue_tasks": overdue_tasks,
        "nearest_task": nearest_task,
        "completion_rate": completion_rate
    }


def get_analytics_data(user):
    tasks = Task.query.filter_by(user_id=user.id).all()
    categories = Category.query.filter_by(user_id=user.id).all()
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.is_done])
    active_tasks = len([t for t in tasks if not t.is_done])

    by_priority = {
        "high": len([x for x in tasks if x.priority == "high"]),
        "medium": len([x for x in tasks if x.priority == "medium"]),
        "low": len([x for x in tasks if x.priority == "low"]),
    }

    by_category = []
    for category in categories:
        category_tasks = [x for x in tasks if x.category_id == category.id]
        by_category.append({
            "name": category.name,
            "count": len(category_tasks),
            "done": len([x for x in category_tasks if x.is_done])
        })

    without_category = [x for x in tasks if x.category_id is None]
    if without_category:
        by_category.append({
            "name": "Без категории",
            "count": len(without_category),
            "done": len([x for x in without_category if x.is_done])
        })

    completion_rate = round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "active_tasks": active_tasks,
        "completion_rate": completion_rate,
        "by_priority": by_priority,
        "by_category": by_category
    }