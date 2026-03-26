import asyncio
import uuid
from app.database import AsyncSessionLocal
from app.models.workout import Exercise


EXERCISES = [
    # PECHO
    {"name": "Press de banca", "muscle_primary": "pecho", "muscle_secondary": ["tríceps", "hombro anterior"], "equipment_type": "barra", "difficulty": "intermediate"},
    {"name": "Press de banca inclinado", "muscle_primary": "pecho", "muscle_secondary": ["tríceps", "hombro anterior"], "equipment_type": "barra", "difficulty": "intermediate"},
    {"name": "Aperturas con mancuernas", "muscle_primary": "pecho", "muscle_secondary": ["hombro anterior"], "equipment_type": "mancuernas", "difficulty": "beginner"},
    {"name": "Fondos en paralelas", "muscle_primary": "pecho", "muscle_secondary": ["tríceps"], "equipment_type": "paralelas", "difficulty": "intermediate"},
    {"name": "Flexiones", "muscle_primary": "pecho", "muscle_secondary": ["tríceps", "hombro anterior"], "equipment_type": "ninguno", "difficulty": "beginner"},

    # ESPALDA
    {"name": "Dominadas", "muscle_primary": "espalda", "muscle_secondary": ["bíceps"], "equipment_type": "barra dominadas", "difficulty": "intermediate"},
    {"name": "Remo con barra", "muscle_primary": "espalda", "muscle_secondary": ["bíceps", "trapecio"], "equipment_type": "barra", "difficulty": "intermediate"},
    {"name": "Remo con mancuerna", "muscle_primary": "espalda", "muscle_secondary": ["bíceps"], "equipment_type": "mancuernas", "difficulty": "beginner"},
    {"name": "Jalón al pecho", "muscle_primary": "espalda", "muscle_secondary": ["bíceps"], "equipment_type": "polea", "difficulty": "beginner"},
    {"name": "Peso muerto", "muscle_primary": "espalda", "muscle_secondary": ["glúteos", "isquios", "trapecio"], "equipment_type": "barra", "difficulty": "advanced"},

    # HOMBROS
    {"name": "Press militar", "muscle_primary": "hombros", "muscle_secondary": ["tríceps"], "equipment_type": "barra", "difficulty": "intermediate"},
    {"name": "Press con mancuernas", "muscle_primary": "hombros", "muscle_secondary": ["tríceps"], "equipment_type": "mancuernas", "difficulty": "beginner"},
    {"name": "Elevaciones laterales", "muscle_primary": "hombros", "muscle_secondary": [], "equipment_type": "mancuernas", "difficulty": "beginner"},
    {"name": "Elevaciones frontales", "muscle_primary": "hombros", "muscle_secondary": [], "equipment_type": "mancuernas", "difficulty": "beginner"},
    {"name": "Pájaros", "muscle_primary": "hombros", "muscle_secondary": ["trapecio"], "equipment_type": "mancuernas", "difficulty": "beginner"},

    # PIERNAS
    {"name": "Sentadilla", "muscle_primary": "cuádriceps", "muscle_secondary": ["glúteos", "isquios"], "equipment_type": "barra", "difficulty": "intermediate"},
    {"name": "Sentadilla frontal", "muscle_primary": "cuádriceps", "muscle_secondary": ["glúteos"], "equipment_type": "barra", "difficulty": "advanced"},
    {"name": "Prensa de piernas", "muscle_primary": "cuádriceps", "muscle_secondary": ["glúteos", "isquios"], "equipment_type": "máquina", "difficulty": "beginner"},
    {"name": "Extensión de cuádriceps", "muscle_primary": "cuádriceps", "muscle_secondary": [], "equipment_type": "máquina", "difficulty": "beginner"},
    {"name": "Curl de isquios", "muscle_primary": "isquiotibiales", "muscle_secondary": [], "equipment_type": "máquina", "difficulty": "beginner"},
    {"name": "Peso muerto rumano", "muscle_primary": "isquiotibiales", "muscle_secondary": ["glúteos"], "equipment_type": "barra", "difficulty": "intermediate"},
    {"name": "Hip thrust", "muscle_primary": "glúteos", "muscle_secondary": ["isquios"], "equipment_type": "barra", "difficulty": "intermediate"},
    {"name": "Zancadas", "muscle_primary": "cuádriceps", "muscle_secondary": ["glúteos"], "equipment_type": "mancuernas", "difficulty": "beginner"},
    {"name": "Gemelos de pie", "muscle_primary": "gemelos", "muscle_secondary": [], "equipment_type": "máquina", "difficulty": "beginner"},

    # BÍCEPS
    {"name": "Curl con barra", "muscle_primary": "bíceps", "muscle_secondary": ["antebrazo"], "equipment_type": "barra", "difficulty": "beginner"},
    {"name": "Curl con mancuernas", "muscle_primary": "bíceps", "muscle_secondary": ["antebrazo"], "equipment_type": "mancuernas", "difficulty": "beginner"},
    {"name": "Curl martillo", "muscle_primary": "bíceps", "muscle_secondary": ["braquial", "antebrazo"], "equipment_type": "mancuernas", "difficulty": "beginner"},
    {"name": "Curl en polea", "muscle_primary": "bíceps", "muscle_secondary": [], "equipment_type": "polea", "difficulty": "beginner"},

    # TRÍCEPS
    {"name": "Press francés", "muscle_primary": "tríceps", "muscle_secondary": [], "equipment_type": "barra", "difficulty": "intermediate"},
    {"name": "Extensión en polea", "muscle_primary": "tríceps", "muscle_secondary": [], "equipment_type": "polea", "difficulty": "beginner"},
    {"name": "Fondos en banco", "muscle_primary": "tríceps", "muscle_secondary": [], "equipment_type": "banco", "difficulty": "beginner"},

    # ABDOMEN
    {"name": "Crunch", "muscle_primary": "abdomen", "muscle_secondary": [], "equipment_type": "ninguno", "difficulty": "beginner"},
    {"name": "Plancha", "muscle_primary": "abdomen", "muscle_secondary": ["core"], "equipment_type": "ninguno", "difficulty": "beginner"},
    {"name": "Rueda abdominal", "muscle_primary": "abdomen", "muscle_secondary": ["core"], "equipment_type": "rueda", "difficulty": "intermediate"},
    {"name": "Elevación de piernas", "muscle_primary": "abdomen", "muscle_secondary": ["flexores de cadera"], "equipment_type": "ninguno", "difficulty": "intermediate"},
]


async def seed_exercises():
    async with AsyncSessionLocal() as db:
        for ex in EXERCISES:
            exercise = Exercise(
                id=str(uuid.uuid4()),
                name=ex["name"],
                muscle_primary=ex["muscle_primary"],
                muscle_secondary=ex.get("muscle_secondary", []),
                equipment_type=ex.get("equipment_type"),
                difficulty=ex["difficulty"],
                instructions=None,
            )
            db.add(exercise)
        await db.commit()
        print(f"✅ {len(EXERCISES)} ejercicios insertados correctamente")


if __name__ == "__main__":
    asyncio.run(seed_exercises())