from .. import settings
from .eightball import eightball_options
from .funny_text import owoify
from .fuzzy import fuz
from .redis import SuperRedis
from .voice import get_voice_client, get_user_voice_channel, prompt_video_choice

R = SuperRedis(host=settings.SUPER_REDIS_HOST, port=settings.SUPER_REDIS_PORT,)

superheroes = [
    'Ant-Man',
    'Aquaman',
    'Asterix',
    'The Atom',
    'Batgirl',
    'Batman',
    'Batwoman',
    'Black Canary',
    'Black Panther',
    'Captain America',
    'Captain Marvel',
    'Catwoman',
    'Conan the Barbarian',
    'Daredevil',
    'Doc Savage',
    'Doctor Strange',
    'Elektra',
    'Ghost Rider',
    'Green Arrow',
    'Green Lantern',
    'Hawkeye',
    'Hellboy',
    'Incredible Hulk',
    'Iron Fist',
    'Iron Man',
    'Marvelman',
    'Robin',
    'The Rocketeer',
    'The Shadow',
    'Spider-Man',
    'Sub-Mariner',
    'Supergirl',
    'Superman',
    'A Teenage Mutant Ninja Turtle',
    'Thor',
    'The Wasp',
    'Watchmen',
    'Wolverine',
    'Wonder Woman',
    'X-Men',
    'Zatanna',
    'Zatara',
]
