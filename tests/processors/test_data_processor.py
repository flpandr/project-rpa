import pytest
from src.processors.data_processor import DataProcessor
from src.models.user import User
from src.models.post import Post
from src.utils.exceptions import ProcessingError

@pytest.fixture
def data_processor():
    return DataProcessor()

@pytest.fixture
def sample_users_data():
    return [
        {"id": 1, "name": "Test User 1", "username": "test1", "email": "test1@example.com"},
        {"id": 2, "name": "Test User 2", "username": "test2", "email": "test2@example.com"}
    ]

@pytest.fixture
def sample_posts_data():
    return [
        {"id": 1, "userId": 1, "title": "Post 1", "body": "Content 1"},
        {"id": 2, "userId": 1, "title": "Post 2", "body": "Content 2"},
        {"id": 3, "userId": 2, "title": "Post 3", "body": "Content 3"}
    ]

def test_process_users(data_processor, sample_users_data):
    users = data_processor.process_users(sample_users_data)
    assert len(users) == 2
    assert all(isinstance(user, User) for user in users)
    assert users[0].name == "Test User 1"

def test_process_users_invalid_data(data_processor):
    invalid_data = [{"id": 1}]  # Missing required fields
    users = data_processor.process_users(invalid_data)
    assert len(users) == 0

def test_process_posts(data_processor, sample_posts_data):
    posts = data_processor.process_posts(sample_posts_data)
    assert len(posts) == 3
    assert all(isinstance(post, Post) for post in posts)
    assert posts[0].title == "Post 1"

def test_calculate_metrics(data_processor):
    user = User(id=1, name="Test", username="test", email="test@example.com")
    posts = [
        Post(id=1, user_id=1, title="Post 1", body="Content 1"),
        Post(id=2, user_id=1, title="Post 2", body="Content 2")
    ]
    
    updated_user = data_processor.calculate_metrics(user, posts)
    assert updated_user.post_count == 2
    assert updated_user.avg_chars > 0

def test_calculate_metrics_no_posts(data_processor):
    user = User(id=1, name="Test", username="test", email="test@example.com")
    updated_user = data_processor.calculate_metrics(user, [])
    assert updated_user.post_count == 0
    assert updated_user.avg_chars == 0
