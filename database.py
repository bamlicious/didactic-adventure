"""
Comprehensive Technology Education & Learning Database
A complete database system for managing technology resources, courses, 
learning paths, and community collaboration.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ResourceType(Enum):
    """Types of learning resources available."""
    TUTORIAL = "tutorial"
    COURSE = "course"
    DOCUMENTATION = "documentation"
    ARTICLE = "article"
    VIDEO = "video"
    PROJECT = "project"
    TOOL = "tool"
    BOOK = "book"
    WEBINAR = "webinar"
    PODCAST = "podcast"


class SkillLevel(Enum):
    """Skill levels for learning resources."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TechDatabase:
    """
    Main database class for managing technology education resources.
    Handles all CRUD operations and database management.
    """

    def __init__(self, db_path: str = "tech_education.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.init_database()

    def init_database(self) -> None:
        """Initialize database connection and create tables if they don't exist."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self.create_tables()
            print(f"✓ Database initialized: {self.db_path}")
        except sqlite3.Error as e:
            print(f"✗ Database connection error: {e}")
            raise

    def create_tables(self) -> None:
        """Create all necessary database tables."""
        tables = [
            self._create_users_table(),
            self._create_technologies_table(),
            self._create_resources_table(),
            self._create_courses_table(),
            self._create_learning_paths_table(),
            self._create_user_progress_table(),
            self._create_community_projects_table(),
            self._create_community_members_table(),
            self._create_discussions_table(),
            self._create_bookmarks_table(),
            self._create_ratings_table(),
        ]

        for table_sql in tables:
            try:
                self.cursor.execute(table_sql)
            except sqlite3.OperationalError:
                pass  # Table already exists

        self.connection.commit()

    @staticmethod
    def _create_users_table() -> str:
        """SQL for users table."""
        return """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            bio TEXT,
            profile_picture_url TEXT,
            skill_level TEXT DEFAULT 'beginner',
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        """

    @staticmethod
    def _create_technologies_table() -> str:
        """SQL for technologies table."""
        return """
        CREATE TABLE IF NOT EXISTS technologies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            icon_url TEXT,
            official_website TEXT,
            documentation_url TEXT,
            difficulty_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """

    @staticmethod
    def _create_resources_table() -> str:
        """SQL for learning resources table."""
        return """
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            resource_type TEXT NOT NULL,
            technology_id INTEGER,
            skill_level TEXT NOT NULL,
            url TEXT NOT NULL,
            author TEXT,
            duration_minutes INTEGER,
            free BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            view_count INTEGER DEFAULT 0,
            FOREIGN KEY (technology_id) REFERENCES technologies(id)
        )
        """

    @staticmethod
    def _create_courses_table() -> str:
        """SQL for courses table."""
        return """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            instructor TEXT NOT NULL,
            technology_id INTEGER,
            skill_level TEXT NOT NULL,
            duration_hours REAL,
            price REAL DEFAULT 0,
            url TEXT NOT NULL,
            total_modules INTEGER,
            rating REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (technology_id) REFERENCES technologies(id)
        )
        """

    @staticmethod
    def _create_learning_paths_table() -> str:
        """SQL for learning paths table."""
        return """
        CREATE TABLE IF NOT EXISTS learning_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            skill_level TEXT NOT NULL,
            estimated_hours REAL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """

    @staticmethod
    def _create_user_progress_table() -> str:
        """SQL for tracking user progress."""
        return """
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER,
            course_id INTEGER,
            learning_path_id INTEGER,
            progress_percentage REAL DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            hours_spent REAL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES resources(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (learning_path_id) REFERENCES learning_paths(id)
        )
        """

    @staticmethod
    def _create_community_projects_table() -> str:
        """SQL for community projects."""
        return """
        CREATE TABLE IF NOT EXISTS community_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            creator_id INTEGER NOT NULL,
            technology_ids TEXT,
            repository_url TEXT,
            difficulty_level TEXT,
            members_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
        """

    @staticmethod
    def _create_community_members_table() -> str:
        """SQL for community project members."""
        return """
        CREATE TABLE IF NOT EXISTS community_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT DEFAULT 'contributor',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES community_projects(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(project_id, user_id)
        )
        """

    @staticmethod
    def _create_discussions_table() -> str:
        """SQL for community discussions."""
        return """
        CREATE TABLE IF NOT EXISTS discussions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            creator_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            replies_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES community_projects(id),
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
        """

    @staticmethod
    def _create_bookmarks_table() -> str:
        """SQL for user bookmarks."""
        return """
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER,
            course_id INTEGER,
            project_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES resources(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (project_id) REFERENCES community_projects(id)
        )
        """

    @staticmethod
    def _create_ratings_table() -> str:
        """SQL for resource ratings and reviews."""
        return """
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_id INTEGER,
            course_id INTEGER,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (resource_id) REFERENCES resources(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
        """

    # ============== USER OPERATIONS ==============

    def create_user(self, username: str, email: str, password_hash: str, 
                   full_name: str = None, skill_level: str = "beginner") -> int:
        """Create a new user."""
        try:
            self.cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, skill_level)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, full_name, skill_level))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"✗ User creation failed: {e}")
            return None

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row, "users") if row else None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row, "users") if row else None

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information."""
        allowed_fields = ['full_name', 'bio', 'skill_level', 'last_login', 'is_active']
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not fields:
            return False

        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        values = list(fields.values()) + [user_id]
        
        try:
            self.cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ User update failed: {e}")
            return False

    # ============== TECHNOLOGY OPERATIONS ==============

    def create_technology(self, name: str, category: str, description: str = None,
                         official_website: str = None, documentation_url: str = None) -> int:
        """Create a new technology entry."""
        try:
            self.cursor.execute("""
                INSERT INTO technologies (name, category, description, official_website, documentation_url)
                VALUES (?, ?, ?, ?, ?)
            """, (name, category, description, official_website, documentation_url))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            print(f"✗ Technology creation failed: {e}")
            return None

    def get_technology(self, tech_id: int) -> Optional[Dict]:
        """Get technology by ID."""
        self.cursor.execute("SELECT * FROM technologies WHERE id = ?", (tech_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row, "technologies") if row else None

    def search_technologies(self, search_term: str) -> List[Dict]:
        """Search technologies by name or category."""
        self.cursor.execute("""
            SELECT * FROM technologies 
            WHERE name LIKE ? OR category LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%"))
        return [self._row_to_dict(row, "technologies") for row in self.cursor.fetchall()]

    # ============== RESOURCE OPERATIONS ==============

    def create_resource(self, title: str, description: str, resource_type: str,
                       skill_level: str, url: str, author: str = None,
                       technology_id: int = None, duration_minutes: int = None,
                       free: bool = True) -> int:
        """Create a new learning resource."""
        try:
            self.cursor.execute("""
                INSERT INTO resources (title, description, resource_type, technology_id, 
                                      skill_level, url, author, duration_minutes, free)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, resource_type, technology_id, skill_level, 
                  url, author, duration_minutes, free))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"✗ Resource creation failed: {e}")
            return None

    def get_resource(self, resource_id: int) -> Optional[Dict]:
        """Get resource by ID."""
        self.cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row, "resources") if row else None

    def search_resources(self, search_term: str = None, skill_level: str = None,
                        resource_type: str = None, technology_id: int = None) -> List[Dict]:
        """Search resources with multiple filters."""
        query = "SELECT * FROM resources WHERE 1=1"
        params = []

        if search_term:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        if skill_level:
            query += " AND skill_level = ?"
            params.append(skill_level)
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        if technology_id:
            query += " AND technology_id = ?"
            params.append(technology_id)

        self.cursor.execute(query, params)
        return [self._row_to_dict(row, "resources") for row in self.cursor.fetchall()]

    def increment_resource_views(self, resource_id: int) -> bool:
        """Increment view count for a resource."""
        try:
            self.cursor.execute(
                "UPDATE resources SET view_count = view_count + 1 WHERE id = ?",
                (resource_id,)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Failed to increment views: {e}")
            return False

    # ============== COURSE OPERATIONS ==============

    def create_course(self, title: str, description: str, instructor: str,
                     skill_level: str, url: str, technology_id: int = None,
                     duration_hours: float = None, price: float = 0, 
                     total_modules: int = None, rating: float = None) -> int:
        """Create a new course."""
        try:
            self.cursor.execute("""
                INSERT INTO courses (title, description, instructor, technology_id,
                                    skill_level, url, duration_hours, price, total_modules, rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, instructor, technology_id, skill_level, url,
                  duration_hours, price, total_modules, rating))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"✗ Course creation failed: {e}")
            return None

    def get_course(self, course_id: int) -> Optional[Dict]:
        """Get course by ID."""
        self.cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row, "courses") if row else None

    def search_courses(self, search_term: str = None, skill_level: str = None,
                      technology_id: int = None, free_only: bool = False) -> List[Dict]:
        """Search courses with filters."""
        query = "SELECT * FROM courses WHERE 1=1"
        params = []

        if search_term:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        if skill_level:
            query += " AND skill_level = ?"
            params.append(skill_level)
        if technology_id:
            query += " AND technology_id = ?"
            params.append(technology_id)
        if free_only:
            query += " AND price = 0"

        self.cursor.execute(query, params)
        return [self._row_to_dict(row, "courses") for row in self.cursor.fetchall()]

    # ============== LEARNING PATH OPERATIONS ==============

    def create_learning_path(self, title: str, description: str, skill_level: str,
                            created_by: int, estimated_hours: float = None) -> int:
        """Create a new learning path."""
        try:
            self.cursor.execute("""
                INSERT INTO learning_paths (title, description, skill_level, created_by, estimated_hours)
                VALUES (?, ?, ?, ?, ?)
            """, (title, description, skill_level, created_by, estimated_hours))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"✗ Learning path creation failed: {e}")
            return None

    def get_learning_path(self, path_id: int) -> Optional[Dict]:
        """Get learning path by ID."""
        self.cursor.execute("SELECT * FROM learning_paths WHERE id = ?", (path_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row, "learning_paths") if row else None

    def get_learning_paths_by_skill_level(self, skill_level: str) -> List[Dict]:
        """Get all learning paths for a specific skill level."""
        self.cursor.execute(
            "SELECT * FROM learning_paths WHERE skill_level = ? ORDER BY created_at DESC",
            (skill_level,)
        )
        return [self._row_to_dict(row, "learning_paths") for row in self.cursor.fetchall()]

    # ============== USER PROGRESS OPERATIONS ==============

    def track_user_progress(self, user_id: int, progress_percentage: float = 0,
                           resource_id: int = None, course_id: int = None,
                           learning_path_id: int = None) -> int:
        """Track user progress on a resource/course/learning path."""
        try:
            self.cursor.execute("""
                INSERT INTO user_progress (user_id, resource_id, course_id, learning_path_id, progress_percentage)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, resource_id, course_id, learning_path_id, progress_percentage))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"✗ Progress tracking failed: {e}")
            return None

    def update_user_progress(self, progress_id: int, progress_percentage: float,
                            hours_spent: float = None, completed: bool = False) -> bool:
        """Update user progress."""
        try:
            if completed:
                self.cursor.execute("""
                    UPDATE user_progress 
                    SET progress_percentage = ?, hours_spent = ?, completed = 1, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (progress_percentage, hours_spent or 0, progress_id))
            else:
                self.cursor.execute("""
                    UPDATE user_progress 
                    SET progress_percentage = ?, hours_spent = ?
                    WHERE id = ?
                """, (progress_percentage, hours_spent or 0, progress_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Progress update failed: {e}")
            return False

    def get_user_progress(self, user_id: int) -> List[Dict]:
        """Get all progress records for a user."""
        self.cursor.execute("SELECT * FROM user_progress WHERE user_id = ?", (user_id,))
        return [self._row_to_dict(row, "user_progress") for row in self.cursor.fetchall()]

    # ============== COMMUNITY PROJECT OPERATIONS ==============

    def create_community_project(self, title: str, description: str, creator_id: int,
                                repository_url: str = None, technology_ids: List[int] = None,
                                difficulty_level: str = "intermediate") -> int:
        """Create a new community project."""
        try:
            tech_ids_str = json.dumps(technology_ids) if technology_ids else None
            self.cursor.execute("""
                INSERT INTO community_projects (title, description, creator_id, repository_url, 
                                               technology_ids, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, description, creator_id, repository_url, tech_ids_str, difficulty_level))
            self.connection.commit()
            project_id = self.cursor.lastrowid
            # Add creator as a member
            self.add_community_member(project_id, creator_id, "creator")
            return project_id
        except sqlite3.Error as e:
            print(f"✗ Community project creation failed: {e}")
            return None

    def get_community_project(self, project_id: int) -> Optional[Dict]:
        """Get community project by ID."""
        self.cursor.execute("SELECT * FROM community_projects WHERE id = ?", (project_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row, "community_projects") if row else None

    def get_active_community_projects(self, limit: int = 50) -> List[Dict]:
        """Get all active community projects."""
        self.cursor.execute("""
            SELECT * FROM community_projects WHERE status = 'active' 
            ORDER BY updated_at DESC LIMIT ?
        """, (limit,))
        return [self._row_to_dict(row, "community_projects") for row in self.cursor.fetchall()]

    def add_community_member(self, project_id: int, user_id: int, role: str = "contributor") -> bool:
        """Add a member to a community project."""
        try:
            self.cursor.execute("""
                INSERT INTO community_members (project_id, user_id, role)
                VALUES (?, ?, ?)
            """, (project_id, user_id, role))
            self.connection.commit()
            # Update member count
            self.cursor.execute(
                "UPDATE community_projects SET members_count = members_count + 1 WHERE id = ?",
                (project_id,)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # User already a member
        except sqlite3.Error as e:
            print(f"✗ Failed to add community member: {e}")
            return False

    def get_project_members(self, project_id: int) -> List[Dict]:
        """Get all members of a community project."""
        self.cursor.execute("""
            SELECT u.*, cm.role FROM users u 
            JOIN community_members cm ON u.id = cm.user_id 
            WHERE cm.project_id = ?
        """, (project_id,))
        return [self._row_to_dict(row, "users") for row in self.cursor.fetchall()]

    # ============== DISCUSSION OPERATIONS ==============

    def create_discussion(self, title: str, content: str, creator_id: int,
                         project_id: int = None) -> int:
        """Create a new discussion."""
        try:
            self.cursor.execute("""
                INSERT INTO discussions (title, content, creator_id, project_id)
                VALUES (?, ?, ?, ?)
            """, (title, content, creator_id, project_id))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"✗ Discussion creation failed: {e}")
            return None

    def get_discussion(self, discussion_id: int) -> Optional[Dict]:
        """Get discussion by ID."""
        self.cursor.execute("SELECT * FROM discussions WHERE id = ?", (discussion_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row, "discussions") if row else None

    def get_project_discussions(self, project_id: int) -> List[Dict]:
        """Get all discussions for a project."""
        self.cursor.execute("""
            SELECT * FROM discussions WHERE project_id = ? 
            ORDER BY created_at DESC
        """, (project_id,))
        return [self._row_to_dict(row, "discussions") for row in self.cursor.fetchall()]

    # ============== BOOKMARK OPERATIONS ==============

    def add_bookmark(self, user_id: int, resource_id: int = None, course_id: int = None,
                    project_id: int = None) -> bool:
        """Add a bookmark for a user."""
        try:
            self.cursor.execute("""
                INSERT INTO bookmarks (user_id, resource_id, course_id, project_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, resource_id, course_id, project_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Bookmark creation failed: {e}")
            return False

    def get_user_bookmarks(self, user_id: int) -> List[Dict]:
        """Get all bookmarks for a user."""
        self.cursor.execute("SELECT * FROM bookmarks WHERE user_id = ?", (user_id,))
        return [self._row_to_dict(row, "bookmarks") for row in self.cursor.fetchall()]

    def remove_bookmark(self, bookmark_id: int) -> bool:
        """Remove a bookmark."""
        try:
            self.cursor.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Bookmark removal failed: {e}")
            return False

    # ============== RATING OPERATIONS ==============

    def add_rating(self, user_id: int, rating: int, review_text: str = None,
                  resource_id: int = None, course_id: int = None) -> bool:
        """Add a rating and review."""
        if not (1 <= rating <= 5):
            print("✗ Rating must be between 1 and 5")
            return False

        try:
            self.cursor.execute("""
                INSERT INTO ratings (user_id, rating, review_text, resource_id, course_id)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, rating, review_text, resource_id, course_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"✗ Rating creation failed: {e}")
            return False

    def get_resource_ratings(self, resource_id: int) -> List[Dict]:
        """Get all ratings for a resource."""
        self.cursor.execute(
            "SELECT * FROM ratings WHERE resource_id = ? ORDER BY created_at DESC",
            (resource_id,)
        )
        return [self._row_to_dict(row, "ratings") for row in self.cursor.fetchall()]

    def get_average_rating(self, resource_id: int = None, course_id: int = None) -> float:
        """Get average rating for a resource or course."""
        if resource_id:
            self.cursor.execute("SELECT AVG(rating) FROM ratings WHERE resource_id = ?", (resource_id,))
        elif course_id:
            self.cursor.execute("SELECT AVG(rating) FROM ratings WHERE course_id = ?", (course_id,))
        else:
            return 0.0

        result = self.cursor.fetchone()[0]
        return result or 0.0

    # ============== UTILITY METHODS ==============

    def _row_to_dict(self, row: Tuple, table_name: str) -> Dict:
        """Convert a database row to a dictionary."""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in self.cursor.fetchall()]
        return dict(zip(columns, row))

    def get_statistics(self) -> Dict:
        """Get overall database statistics."""
        stats = {}

        tables = ['users', 'resources', 'courses', 'learning_paths', 'community_projects', 'discussions']
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = self.cursor.fetchone()[0]

        return stats

    def export_data(self, output_file: str) -> bool:
        """Export all data to a JSON file."""
        try:
            data = {}
            for table in ['users', 'resources', 'courses', 'learning_paths', 
                         'community_projects', 'discussions', 'user_progress']:
                self.cursor.execute(f"SELECT * FROM {table}")
                rows = self.cursor.fetchall()
                self.cursor.execute(f"PRAGMA table_info({table})")
                columns = [column[1] for column in self.cursor.fetchall()]
                data[table] = [dict(zip(columns, row)) for row in rows]

            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"✓ Data exported to {output_file}")
            return True
        except Exception as e:
            print(f"✗ Export failed: {e}")
            return False

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")


# ============== EXAMPLE USAGE ==============

if __name__ == "__main__":
    # Initialize database
    db = TechDatabase()

    # Create a user
    user_id = db.create_user(
        username="john_learner",
        email="john@example.com",
        password_hash="hashed_password",
        full_name="John Learner",
        skill_level="beginner"
    )
    print(f"✓ User created with ID: {user_id}")

    # Create technologies
    python_id = db.create_technology(
        name="Python",
        category="Programming Language",
        description="A versatile programming language",
        official_website="https://python.org",
        documentation_url="https://docs.python.org"
    )

    react_id = db.create_technology(
        name="React",
        category="JavaScript Library",
        description="A JavaScript library for building UIs",
        official_website="https://react.dev",
        documentation_url="https://react.dev/learn"
    )

    # Create learning resources
    resource_id = db.create_resource(
        title="Python for Beginners",
        description="Learn Python basics",
        resource_type="tutorial",
        skill_level="beginner",
        url="https://example.com/python-tutorial",
        author="John Doe",
        technology_id=python_id,
        duration_minutes=120,
        free=True
    )

    # Create a course
    course_id = db.create_course(
        title="Advanced Python Development",
        description="Master advanced Python concepts",
        instructor="Jane Smith",
        skill_level="advanced",
        url="https://example.com/advanced-python",
        technology_id=python_id,
        duration_hours=40,
        price=0,
        total_modules=20,
        rating=4.8
    )

    # Create a learning path
    path_id = db.create_learning_path(
        title="Web Development Path",
        description="Learn web development from scratch",
        skill_level="beginner",
        created_by=user_id,
        estimated_hours=100
    )

    # Track user progress
    progress_id = db.track_user_progress(
        user_id=user_id,
        resource_id=resource_id,
        progress_percentage=50
    )

    # Create a community project
    project_id = db.create_community_project(
        title="Open Source AI Tools",
        description="Building accessible AI tools for everyone",
        creator_id=user_id,
        repository_url="https://github.com/example/ai-tools",
        technology_ids=[python_id],
        difficulty_level="advanced"
    )

    # Add bookmark
    db.add_bookmark(user_id=user_id, resource_id=resource_id)

    # Add rating
    db.add_rating(user_id=user_id, resource_id=resource_id, rating=5, review_text="Great tutorial!")

    # Display statistics
    stats = db.get_statistics()
    print("\n📊 Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Export data
    db.export_data("tech_education_data.json")

    # Close connection
    db.close()
