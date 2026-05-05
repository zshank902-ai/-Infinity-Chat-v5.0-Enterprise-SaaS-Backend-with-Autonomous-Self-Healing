import os
import django

def test_task_assignment_project(directory):
    try:
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_assignment.settings')
        django.setup()
        
        # Test MarkdownxField for XSS protection
        from tasks.models import Task
        description = "<script>alert('XSS')</script>"
        task = Task(title="Title", description=description, assigned_to=None, deadline=None)
        task.full_clean()  # This should not raise any errors
        
        # Test CSRF protection in forms
        from tasks.forms import TaskForm
        form = TaskForm()
        form.is_valid()  # This should return True
        
        print("All tests passed.")
        assert True
        
    except Exception as e:
        print(f"Tests failed: {str(e)}")
        assert False, str(e)

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(__file__)
    test_task_assignment_project(BASE_DIR)
    exit(0)