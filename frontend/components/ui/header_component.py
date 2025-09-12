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
    - Consistent A101 branding with corporate colors
    - Navigation menu with active state using Tabs
    - User information display in a dropdown menu
    - Logout functionality
    - Clean, modern, and functional design
    """

    def __init__(self, api_client):
        self.api_client = api_client
        self.nav_tabs = None
        self.user_full_name_label = None
        self.user_title_label = None

    async def render(self, current_page: Optional[str] = "home") -> None:
        """
        @doc
        Render the unified header with navigation.

        Args:
            current_page: Current page identifier for navigation highlighting
        """
        with ui.header(elevated=True).classes(
            "bg-primary text-white px-8 py-2 shadow-md"
        ) as header:
            with ui.row().classes("w-full items-center justify-between"):
                self._render_logo()
                self._render_navigation(current_page)
                self._render_user_menu()

    def _render_logo(self):
        """Renders the logo and application title."""
        with ui.row().classes("items-center gap-3 cursor-pointer") as logo:
            ui.icon("business_center", size="2rem").classes("text-white")
            ui.label("A101 HR").classes("text-xl font-bold")
        logo.on("click", lambda: ui.navigate.to("/"))

    def _render_navigation(self, current_page: str):
        """Renders the main navigation tabs."""
        nav_items = [
            {"key": "home", "label": "Главная", "path": "/"},
            {"key": "generator", "label": "Генератор", "path": "/generator"},
            {"key": "profiles", "label": "Профили", "path": "/profiles"},
            {"key": "analytics", "label": "Аналитика", "path": "/analytics"},
        ]

        with ui.tabs(value=current_page).classes("text-white") as self.nav_tabs:
            for item in nav_items:
                ui.tab(name=item["key"], label=item["label"]).on(
                    "click", lambda path=item["path"]: ui.navigate.to(path)
                )

    def _render_user_menu(self):
        """Renders the user menu directly in the header without a dropdown."""
        user_info = app.storage.user.get("user_info", {})
        full_name = user_info.get("full_name", "Пользователь")
        title = user_info.get("title", "Сотрудник")
        initials = "".join([name[0] for name in full_name.split()[:2]]).upper()

        with ui.row().classes("items-center gap-4"):
            # Avatar
            with ui.avatar(size="md", color="white", text_color="primary"):
                ui.label(initials).classes("text-md font-bold")

            # User Info
            with ui.column().classes("gap-0 leading-tight"):
                ui.label(full_name).classes("font-semibold text-sm")
                ui.label(title).classes("text-xs opacity-80")

            # Logout Button
            ui.button(icon="logout", on_click=self._handle_logout).props(
                "flat round dense"
            ).classes("text-white").tooltip("Выйти из системы")

    def update_user_info(self):
        """Updates the user info in the header after login."""
        # This component is re-rendered on navigation, so direct update isn't strictly necessary
        # but can be implemented if needed for single-page updates.
        pass

    async def _handle_logout(self):
        """Handle user logout with proper cleanup."""
        try:
            await self.api_client.logout()
        except Exception as e:
            logger.error(f"Backend logout error: {e}")

        app.storage.user.clear()
        ui.notify("Вы вышли из системы", type="positive")
        ui.navigate.to("/login")


if __name__ == "__main__":
    print("✅ HeaderComponent created successfully!")
    print("🧭 Features:")
    print("  - Unified navigation across all pages")
    print("  - Active page highlighting")
    print("  - User information display")
    print("  - Consistent A101 branding")
