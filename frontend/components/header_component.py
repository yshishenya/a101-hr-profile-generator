"""
@doc
Unified header component for consistent navigation across all A101 HR pages.

Provides consistent navigation, user info, and logout functionality
that can be reused on all pages of the application.

Examples:
  python> header = HeaderComponent(api_client)
  python> await header.render(current_page="generator")
"""

from nicegui import ui, app
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class HeaderComponent:
    """
    @doc
    Unified header with navigation for all A101 HR pages.

    Features:
    - Consistent A101 branding
    - Navigation menu with active state
    - User information display
    - Logout functionality
    - Responsive design

    Examples:
      python> header = HeaderComponent(api_client)
      python> await header.render(current_page="generator")
    """

    def __init__(self, api_client):
        self.api_client = api_client
        self.current_page = "home"

    async def render(self, current_page: Optional[str] = "home") -> None:
        """
        @doc
        Render the unified header with navigation.

        Args:
            current_page: Current page identifier for navigation highlighting

        Examples:
          python> await header.render("generator")
        """
        self.current_page = current_page

        # Get user information
        user_info = app.storage.user.get("user_info", {})
        username = user_info.get("username", "User")
        full_name = user_info.get("full_name", username)

        # Main header with A101 branding
        with ui.header().classes("bg-primary text-white shadow-2"):
            with ui.row().classes("w-full items-center justify-between px-4 py-2"):

                # Left: Logo and navigation
                with ui.row().classes("items-center gap-4"):
                    # A101 Logo and title
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("business", size="1.5rem").classes("text-white")
                        ui.label("A101 HR Profile Generator").classes(
                            "text-h6 font-weight-medium"
                        )

                    # Navigation menu
                    self._create_navigation_menu()

                # Right: User info and logout
                with ui.row().classes("items-center gap-3"):
                    # User avatar and name
                    with ui.row().classes(
                        "items-center gap-2 bg-white bg-opacity-10 rounded px-3 py-1"
                    ):
                        ui.avatar(icon="person", color="white", size="sm").classes(
                            "text-primary"
                        )
                        ui.label(f"{full_name}").classes(
                            "text-subtitle2 font-weight-medium"
                        )

                    # Logout button
                    ui.button(
                        "Выйти", icon="logout", on_click=self._handle_logout
                    ).props("flat dense").classes("text-white").tooltip(
                        "Выйти из системы"
                    )

    def _create_navigation_menu(self):
        """Create navigation buttons with active state highlighting"""
        nav_items = [
            {"key": "home", "label": "Главная", "icon": "home", "path": "/"},
            {
                "key": "generator",
                "label": "Генератор",
                "icon": "psychology",
                "path": "/generator",
            },
            {
                "key": "profiles",
                "label": "Профили",
                "icon": "folder",
                "path": "/profiles",
            },
            {
                "key": "history",
                "label": "История",
                "icon": "history",
                "path": "/history",
            },
        ]

        for item in nav_items:
            # Determine if this is the current page
            is_active = self.current_page == item["key"]

            # Button styling based on active state
            button_classes = "text-white font-weight-medium"
            if is_active:
                button_classes += " bg-white bg-opacity-20 text-weight-bold"

            ui.button(
                item["label"],
                icon=item["icon"],
                on_click=lambda path=item["path"]: ui.navigate.to(path),
            ).props("flat dense").classes(button_classes).tooltip(
                f"Перейти: {item['label']}"
            )

    async def _handle_logout(self):
        """Handle user logout with proper cleanup"""
        try:
            # Call backend logout
            await self.api_client.logout()
        except Exception as e:
            logger.error(f"Backend logout error: {e}")

        # Clear local session
        app.storage.user.clear()

        # Notify and redirect
        ui.notify("Вы вышли из системы", type="positive")
        ui.navigate.to("/login")


if __name__ == "__main__":
    print("✅ HeaderComponent created successfully!")
    print("🧭 Features:")
    print("  - Unified navigation across all pages")
    print("  - Active page highlighting")
    print("  - User information display")
    print("  - Consistent A101 branding")
