"""
Seed script to populate the database with realistic test data for dashboard testing.

Run with: uv run python scripts/seed_database.py
"""

import random
from datetime import UTC, date, datetime, timedelta

from day_play.integrations.database.database import SessionLocal, init_db
from day_play.integrations.database.models import (
    Achievement,
    DailyProgress,
    Prize,
    Task,
    User,
)
from day_play.models.enums import Priority, RecurrencePattern, TaskStatus, Urgency


def clear_existing_data(db) -> None:
    """Clear all existing data from tables."""
    db.query(DailyProgress).delete()
    db.query(Achievement).delete()
    db.query(Prize).delete()
    db.query(Task).delete()
    db.query(User).delete()
    db.commit()
    print("✓ Cleared existing data")


def calculate_level_from_xp(total_xp: int) -> int:
    """Calculate the correct level for a given XP amount."""
    base_xp = 100
    level = 1
    while level < 1000:
        if level <= 20:
            xp_needed = int(base_xp * (level ** 1.5))
        elif level <= 50:
            level_20_xp = int(base_xp * ((20 - 1) ** 1.5))
            additional = int(base_xp * ((level - 20) ** 1.3) * 1.8)
            xp_needed = level_20_xp + additional
        else:
            level_20_xp = int(base_xp * ((20 - 1) ** 1.5))
            level_50_xp = level_20_xp + int(base_xp * ((50 - 20) ** 1.3) * 1.8)
            additional = int(base_xp * ((level - 50) ** 1.1) * 2.5)
            xp_needed = level_50_xp + additional
        if total_xp < xp_needed:
            return level
        level += 1
    return level


def seed_users(db) -> list[User]:
    """Create sample users."""
    # Define XP values, levels will be calculated
    user_data = [
        {"id": 1, "username": "alex_productivity", "total_xp": 650},   # Should be ~level 5
        {"id": 2, "username": "sarah_achiever", "total_xp": 2200},     # Should be ~level 8
        {"id": 3, "username": "mike_beginner", "total_xp": 150},       # Should be ~level 2
    ]
    
    users = []
    for data in user_data:
        level = calculate_level_from_xp(data["total_xp"])
        user = User(
            id=data["id"],
            username=data["username"],
            current_level=level,
            total_xp=data["total_xp"],
        )
        users.append(user)
        db.add(user)
    db.commit()
    print(f"✓ Created {len(users)} users")
    return users


def seed_tasks(db, users: list[User]) -> list[Task]:
    """Create sample tasks for each user."""
    now = datetime.now(UTC)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Task templates for realistic variety
    task_templates = [
        # Work tasks
        {"title": "Review quarterly report", "description": "Go through Q4 financial statements", "priority": Priority.HIGH, "urgency": Urgency.HIGH},
        {"title": "Team standup meeting", "description": "Daily sync with the team", "priority": Priority.MEDIUM, "urgency": Urgency.HIGH, "recurrence": RecurrencePattern.DAILY},
        {"title": "Update project documentation", "description": "Keep docs up to date", "priority": Priority.LOW, "urgency": Urgency.LOW},
        {"title": "Code review for PR #42", "description": "Review backend changes", "priority": Priority.HIGH, "urgency": Urgency.MEDIUM},
        {"title": "Prepare presentation slides", "description": "For Friday's client meeting", "priority": Priority.HIGH, "urgency": Urgency.MEDIUM},
        
        # Personal tasks
        {"title": "Morning workout", "description": "30 min cardio + strength", "priority": Priority.MEDIUM, "urgency": Urgency.LOW, "recurrence": RecurrencePattern.DAILY},
        {"title": "Grocery shopping", "description": "Weekly groceries", "priority": Priority.MEDIUM, "urgency": Urgency.MEDIUM, "recurrence": RecurrencePattern.WEEKLY},
        {"title": "Read 20 pages", "description": "Current book: Atomic Habits", "priority": Priority.LOW, "urgency": Urgency.LOW, "recurrence": RecurrencePattern.DAILY},
        {"title": "Call mom", "description": "Weekly family check-in", "priority": Priority.MEDIUM, "urgency": Urgency.LOW, "recurrence": RecurrencePattern.WEEKLY},
        {"title": "Meditate for 10 minutes", "description": "Mindfulness practice", "priority": Priority.LOW, "urgency": Urgency.LOW, "recurrence": RecurrencePattern.DAILY},
        
        # Household
        {"title": "Pay utility bills", "description": "Electricity, water, internet", "priority": Priority.HIGH, "urgency": Urgency.HIGH, "recurrence": RecurrencePattern.MONTHLY},
        {"title": "Clean apartment", "description": "Weekly deep clean", "priority": Priority.MEDIUM, "urgency": Urgency.MEDIUM, "recurrence": RecurrencePattern.WEEKLY},
        {"title": "Laundry", "description": "Wash and fold clothes", "priority": Priority.MEDIUM, "urgency": Urgency.MEDIUM},
        {"title": "Water plants", "description": "Don't let them die!", "priority": Priority.LOW, "urgency": Urgency.LOW, "recurrence": RecurrencePattern.WEEKLY},
        
        # Learning
        {"title": "Complete Python course module", "description": "Chapter 5: Async programming", "priority": Priority.MEDIUM, "urgency": Urgency.LOW},
        {"title": "Practice Spanish on Duolingo", "description": "15 minutes daily", "priority": Priority.LOW, "urgency": Urgency.LOW, "recurrence": RecurrencePattern.DAILY},
        {"title": "Watch tech conference talk", "description": "PyCon 2024 recordings", "priority": Priority.LOW, "urgency": Urgency.LOW},
        
        # Health
        {"title": "Doctor appointment", "description": "Annual checkup", "priority": Priority.HIGH, "urgency": Urgency.MEDIUM},
        {"title": "Take vitamins", "description": "Daily supplements", "priority": Priority.LOW, "urgency": Urgency.LOW, "recurrence": RecurrencePattern.DAILY},
        {"title": "Drink 8 glasses of water", "description": "Stay hydrated!", "priority": Priority.LOW, "urgency": Urgency.LOW, "recurrence": RecurrencePattern.DAILY},
    ]
    
    all_tasks = []
    
    for user in users:
        # Each user gets a random subset of tasks with different statuses
        user_task_count = random.randint(8, 15)
        selected_templates = random.sample(task_templates, min(user_task_count, len(task_templates)))
        
        for template in selected_templates:
            # Randomize status with weighted distribution
            status_weights = [
                (TaskStatus.COMPLETED, 0.4),
                (TaskStatus.IN_PROGRESS, 0.2),
                (TaskStatus.PENDING, 0.4),
            ]
            status = random.choices(
                [s[0] for s in status_weights],
                weights=[s[1] for s in status_weights]
            )[0]
            
            # Set dates based on status
            created_at = today - timedelta(days=random.randint(1, 30))
            due_date = today + timedelta(days=random.randint(-2, 14))
            completed_at = None
            
            if status == TaskStatus.COMPLETED:
                completed_at = created_at + timedelta(days=random.randint(0, 5))
            
            task = Task(
                title=template["title"],
                description=template.get("description"),
                priority=template["priority"],
                urgency=template["urgency"],
                status=status,
                due_date=due_date,
                recurrence_pattern=template.get("recurrence", RecurrencePattern.NONE),
                custom_xp=random.choice([None, 50, 100, 150]) if random.random() > 0.7 else None,
                created_at=created_at,
                updated_at=now,
                completed_at=completed_at,
                user_id=user.id,
            )
            db.add(task)
            all_tasks.append(task)
    
    db.commit()
    print(f"✓ Created {len(all_tasks)} tasks")
    return all_tasks


def seed_daily_progress(db, users: list[User]) -> list[DailyProgress]:
    """Create daily progress history for each user (last 30 days)."""
    all_progress = []
    today = date.today()
    
    for user in users:
        # Generate 30 days of progress history
        for days_ago in range(30):
            progress_date = today - timedelta(days=days_ago)
            
            # More recent days have higher completion (simulate improvement)
            base_total = random.randint(5, 12)
            
            # Weekends might have fewer tasks
            if progress_date.weekday() >= 5:
                base_total = random.randint(3, 7)
            
            # Completion rate varies by user level and day
            if user.current_level >= 5:
                completion_rate = random.uniform(0.6, 0.95)
            elif user.current_level >= 3:
                completion_rate = random.uniform(0.4, 0.8)
            else:
                completion_rate = random.uniform(0.2, 0.6)
            
            # More recent days tend to be better (learning effect)
            if days_ago < 7:
                completion_rate = min(1.0, completion_rate + 0.1)
            
            tasks_completed = int(base_total * completion_rate)
            completion_percentage = (tasks_completed / base_total * 100) if base_total > 0 else 0
            
            # XP earned based on tasks completed (roughly 25-100 XP per task)
            daily_xp = tasks_completed * random.randint(25, 100)
            
            progress = DailyProgress(
                date=progress_date,
                tasks_completed=tasks_completed,
                tasks_total=base_total,
                completion_percentage=round(completion_percentage, 1),
                daily_xp_earned=daily_xp,
                user_id=user.id,
            )
            db.add(progress)
            all_progress.append(progress)
    
    db.commit()
    print(f"✓ Created {len(all_progress)} daily progress records")
    return all_progress


def seed_achievements(db, users: list[User]) -> list[Achievement]:
    """Create achievements for users."""
    achievement_templates = [
        {
            "name": "First Steps",
            "description": "Complete your first task",
            "icon": "🎯",
            "unlock_criteria": {"tasks_completed": 1},
        },
        {
            "name": "Getting Started",
            "description": "Complete 10 tasks",
            "icon": "⭐",
            "unlock_criteria": {"tasks_completed": 10},
        },
        {
            "name": "Task Master",
            "description": "Complete 50 tasks",
            "icon": "🏆",
            "unlock_criteria": {"tasks_completed": 50},
        },
        {
            "name": "Century Club",
            "description": "Complete 100 tasks",
            "icon": "💯",
            "unlock_criteria": {"tasks_completed": 100},
        },
        {
            "name": "Perfect Day",
            "description": "Complete all tasks in a single day",
            "icon": "🌟",
            "unlock_criteria": {"perfect_day": True},
        },
        {
            "name": "Week Warrior",
            "description": "Complete tasks 7 days in a row",
            "icon": "🔥",
            "unlock_criteria": {"streak_days": 7},
        },
        {
            "name": "Early Bird",
            "description": "Complete a task before 7 AM",
            "icon": "🌅",
            "unlock_criteria": {"early_completion": True},
        },
        {
            "name": "Night Owl",
            "description": "Complete a task after 11 PM",
            "icon": "🦉",
            "unlock_criteria": {"late_completion": True},
        },
        {
            "name": "Level Up!",
            "description": "Reach level 5",
            "icon": "📈",
            "unlock_criteria": {"level": 5},
        },
        {
            "name": "XP Hunter",
            "description": "Earn 1000 XP total",
            "icon": "💎",
            "unlock_criteria": {"total_xp": 1000},
        },
        {
            "name": "Priority Pro",
            "description": "Complete 10 high-priority tasks",
            "icon": "🎖️",
            "unlock_criteria": {"high_priority_completed": 10},
        },
        {
            "name": "Habit Former",
            "description": "Complete a recurring task 10 times",
            "icon": "🔄",
            "unlock_criteria": {"recurring_completions": 10},
        },
    ]
    
    all_achievements = []
    now = datetime.now(UTC)

    for user in users:
        # Higher level users have more achievements unlocked
        if user.current_level >= 8:
            unlock_count = random.randint(8, len(achievement_templates))
        elif user.current_level >= 5:
            unlock_count = random.randint(5, 8)
        else:
            unlock_count = random.randint(2, 4)
        
        # Always include "First Steps" for all users
        selected_achievements = [achievement_templates[0]]  # First Steps
        remaining = list(achievement_templates[1:])
        selected_achievements.extend(random.sample(remaining, min(unlock_count - 1, len(remaining))))
        
        for template in achievement_templates:
            unlocked = template in selected_achievements
            
            achievement = Achievement(
                name=template["name"],
                description=template["description"],
                icon=template["icon"],
                unlock_criteria=template["unlock_criteria"],
                unlocked_at=now - timedelta(days=random.randint(1, 60)) if unlocked else None,
                user_id=user.id,
            )
            db.add(achievement)
            all_achievements.append(achievement)
    
    db.commit()
    print(f"✓ Created {len(all_achievements)} achievements")
    return all_achievements


def seed_prizes(db, users: list[User]) -> list[Prize]:
    """Create prizes for users."""
    prize_templates = [
        {"name": "Coffee Break", "description": "Treat yourself to a nice coffee", "cost_xp": 100},
        {"name": "Movie Night", "description": "Watch your favorite movie guilt-free", "cost_xp": 250},
        {"name": "Gaming Hour", "description": "One hour of gaming time", "cost_xp": 200},
        {"name": "Sleep In", "description": "Sleep in an extra hour", "cost_xp": 300},
        {"name": "Fancy Dinner", "description": "Order from your favorite restaurant", "cost_xp": 500},
        {"name": "New Book", "description": "Buy that book you've been wanting", "cost_xp": 400},
        {"name": "Spa Day", "description": "Relaxation time at the spa", "cost_xp": 1000},
        {"name": "Weekend Trip", "description": "Mini vacation getaway", "cost_xp": 2000},
        {"name": "Tech Gadget", "description": "Small tech purchase", "cost_xp": 1500},
        {"name": "Guilt-Free Netflix", "description": "Binge-watch without guilt", "cost_xp": 150},
        {"name": "Ice Cream Treat", "description": "Your favorite ice cream", "cost_xp": 75},
        {"name": "Social Media Break", "description": "30 min of mindless scrolling", "cost_xp": 50},
    ]
    
    all_prizes = []
    now = datetime.now(UTC)

    for user in users:
        # Each user gets a subset of prizes
        user_prizes = random.sample(prize_templates, random.randint(5, 8))
        
        for template in user_prizes:
            # Some prizes are redeemed based on user's XP history
            can_afford = user.total_xp >= template["cost_xp"]
            redeemed = can_afford and random.random() > 0.6
            
            prize = Prize(
                name=template["name"],
                description=template["description"],
                cost_xp=template["cost_xp"],
                redeemed=redeemed,
                redeemed_at=now - timedelta(days=random.randint(1, 20)) if redeemed else None,
                user_id=user.id,
            )
            db.add(prize)
            all_prizes.append(prize)
    
    db.commit()
    print(f"✓ Created {len(all_prizes)} prizes")
    return all_prizes


def main() -> None:
    """Main function to seed the database."""
    print("\n🌱 Seeding Day-Play database...\n")
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_existing_data(db)
        
        # Seed in order (respecting foreign key constraints)
        users = seed_users(db)
        seed_tasks(db, users)
        seed_daily_progress(db, users)
        seed_achievements(db, users)
        seed_prizes(db, users)
        
        print("\n✅ Database seeding complete!")
        print("\nCreated data for users:")
        for user in users:
            print(f"  • {user.username} (Level {user.current_level}, {user.total_xp} XP)")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
