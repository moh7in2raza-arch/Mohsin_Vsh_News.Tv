from dataclasses import dataclass


@dataclass
class DashboardSummary:
    full_name: str
    role_name: str
    employee_id: str | None
    photo_path: str | None


class DashboardService:

    def __init__(self, user_repository):
        self._users = user_repository

    def get_user_profile(self, username: str):
        return self._users.get_by_username(username)

    def get_dashboard_summary(self, username: str):
        user = self.get_user_profile(username)
        if not user:
            return None

summary = Dashboard_service.get_user_profile(session.username)
self.name_label.setText(summary[full_name]
)
