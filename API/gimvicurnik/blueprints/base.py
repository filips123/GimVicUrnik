from __future__ import annotations

import typing

from flask import Blueprint

if typing.TYPE_CHECKING:
    from typing import ClassVar, Optional
    from flask import Flask
    from ..config import Config


class BaseHandler:
    """Base handler for all application blueprints."""

    name: ClassVar[str]
    """Handler name. Must be set by subclasses.."""

    static_folder: ClassVar[Optional[str]] = None
    """Path to a folder of static files. May be set by subclasses."""

    template_folder: ClassVar[Optional[str]] = None
    """Path to a folder of template files. May be set by subclasses."""

    @classmethod
    def routes(cls, bp: Blueprint, config: Config) -> None:
        """Handler routes. Must be set by subclasses."""
        pass

    @classmethod
    def register(cls, app: Flask, config: Config) -> None:
        """Create a blueprint and register it to the provided app."""

        # Create a blueprint
        bp = Blueprint(
            cls.name,
            "gimvicurnik",
            static_folder=cls.static_folder,
            template_folder=cls.template_folder,
        )

        # Register routes to the blueprint
        cls.routes(bp, config)

        # Register the blueprint to the app
        app.register_blueprint(bp)
