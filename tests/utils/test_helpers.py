import pytest
from src.models.user import User
from src.models.post import Post
from src.utils.helpers import (
    sort_users_by_post_count,
    filter_active_users,
    get_average_post_length
)

@pytest.fixture
def sample_users():
    return [
        User(id=1, name="User 1", username="user1", email="user1@test.com", post_count=5),
        User(id=2, name="User 2", username="user2", email="user2@test.com", post_count=3),
        User(id=3, name="User 3", username="user3", email="user3@test.com", post_count=7),
    ]

@pytest.fixture
def sample_posts():
    return [
        Post(id=1, user_id=1, title="Title 1", body="Content 1"),
        Post(id=2, user_id=1, title="Title 2", body="Longer content 2"),
        Post(id=3, user_id=2, title="Title 3", body="Very long content 3"),
    ]

def test_sort_users_by_post_count(sample_users):
    sorted_users = sort_users_by_post_count(sample_users)
    assert len(sorted_users) == 3
    assert sorted_users[0].post_count == 7
    assert sorted_users[-1].post_count == 3

def test_filter_active_users(sample_users):
    # Test with default min_posts=1
    active_users = filter_active_users(sample_users)
    assert len(active_users) == 3
    
    # Test with higher min_posts threshold
    active_users = filter_active_users(sample_users, min_posts=4)
    assert len(active_users) == 2
    assert all(user.post_count >= 4 for user in active_users)

def test_get_average_post_length(sample_posts):
    avg_length = get_average_post_length(sample_posts)
    expected_avg = sum(len(post.body) for post in sample_posts) / len(sample_posts)
    assert avg_length == expected_avg

def test_get_average_post_length_empty_list():
    avg_length = get_average_post_length([])
    assert avg_length == 0.0
