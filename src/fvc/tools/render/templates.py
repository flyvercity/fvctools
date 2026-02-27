from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader


def generate_html_template(
    title: str,
    generation_time: str,
    file_path: str,
    coordinates: List[Dict[str, Any]],
    bounds: Dict[str, float],
) -> str:
    """Generate the HTML template for the map visualization.

    Args:
        title: Title for the visualization
        generation_time: Timestamp when visualization was generated
        file_path: Name of the input file
        coordinates: List of coordinate data
        bounds: Map bounds dictionary

    Returns:
        HTML content as string
    """
    env = _get_template_env()
    template = env.get_template('report.html.j2')

    return template.render(
        title=title,
        generation_time=generation_time,
        file_path=file_path,
        coordinates=coordinates,
        bounds=bounds,
    )


def generate_js_template() -> str:
    """Generate the JavaScript template for the map functionality.

    Returns:
        JavaScript content as string
    """
    env = _get_template_env()
    template = env.get_template('map.js.j2')

    return template.render()


def _get_template_env() -> Environment:
    """Get Jinja2 environment for template loading.

    Returns:
        Jinja2 Environment instance
    """
    template_dir = Path(__file__).parent / 'templates'
    return Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)
