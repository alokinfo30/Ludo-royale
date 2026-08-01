import asyncio
from app.services.theme_generator import generate_theme

print(asyncio.run(generate_theme('cyberpunk')))
