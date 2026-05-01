from app.schemas.task import TaskCreate, TaskUpdate
from app.services.tasks import (
    create_task,
    get_task,
    update_task,
    delete_task,
    get_focus_tasks,
)


def test_create_task(db):
    task = create_task(db, TaskCreate(title="My Task"))
    assert task.id is not None
    assert task.title == "My Task"
    assert task.is_focus is False
    assert task.is_completed is False


def test_get_task(db):
    task = create_task(db, TaskCreate(title="Task A"))
    fetched = get_task(db, task.id)
    assert fetched.id == task.id


def test_get_task_not_found(db):
    assert get_task(db, 9999) is None


def test_update_task_focus(db):
    task = create_task(db, TaskCreate(title="Focus Me"))
    updated = update_task(db, task.id, TaskUpdate(is_focus=True))
    assert updated.is_focus is True


def test_complete_task(db):
    task = create_task(db, TaskCreate(title="Complete Me"))
    updated = update_task(db, task.id, TaskUpdate(is_completed=True))
    assert updated.is_completed is True


def test_delete_task(db):
    task = create_task(db, TaskCreate(title="Delete Me"))
    assert delete_task(db, task.id) is True
    assert get_task(db, task.id) is None


def test_get_focus_tasks(db):
    create_task(db, TaskCreate(title="Not focus"))
    create_task(db, TaskCreate(title="Focus", is_focus=True))
    focus = get_focus_tasks(db)
    assert len(focus) == 1
    assert focus[0].title == "Focus"


def test_get_focus_tasks_excludes_completed(db):
    create_task(db, TaskCreate(title="Focus Done", is_focus=True, is_completed=True))
    assert len(get_focus_tasks(db)) == 0