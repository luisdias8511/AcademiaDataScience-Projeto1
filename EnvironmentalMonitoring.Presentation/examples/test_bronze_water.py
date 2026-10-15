import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.ingestion.bronze_water_transformer import build_bronze_documents_water
from src.database.reading_repository import ReadingRepository

# Inicializa o repositório conexao com o banco de dados
repository = ReadingRepository()
# Obtem os parâmetros permitidos para parâmetros de água
allowed_parameters = repository.get_parameters_by_CategoryCode("WATER")

# JSON de EXEMPLO retornado pela API Meersens para parâmetros de água
# TEM QUE ESTAR ENTRE ASPAS TRIPLAS (''' ''')
meersens_json = '''
{
    "found": true,
    "values": [
        {
            "datetime": "2026-10-12T17:00:00Z",
            "pollutants": {
                "nitrates": {
                    "found": true,
                    "name": "Nitrates",
                    "shortcode": "N.",
                    "unit": "mg/L",
                    "value": 7.34,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 14.78
                    }
                },
                "pesticides": {
                    "found": true,
                    "name": "Total Pesticides",
                    "shortcode": "T.P.",
                    "unit": "µg/L",
                    "value": 0.187,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Moderate",
                        "icon": null,
                        "color": "#ffb121",
                        "description": "Water of which at least one parameter does not have the optimum concentration or value to guarantee very good quality. Water can still be consumed without risk.",
                        "value": 39.5
                    }
                },
                "arsenic": {
                    "found": true,
                    "name": "Arsenic",
                    "shortcode": "A.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "selenium": {
                    "found": true,
                    "name": "Selenium",
                    "shortcode": "S.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "bromates": {
                    "found": true,
                    "name": "Bromates",
                    "shortcode": "B.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 2,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total aluminium": {
                    "found": true,
                    "name": "Total Aluminium",
                    "shortcode": "Al.",
                    "unit": "µg/L",
                    "value": 4.2,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.21
                    }
                },
                "fluorides": {
                    "found": true,
                    "name": "Fluorides",
                    "shortcode": "Fl.",
                    "unit": "mg/L",
                    "value": 0.54,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Conservative for teeth",
                        "value": 0.2
                    }
                },
                "barium": {
                    "found": true,
                    "name": "Barium",
                    "shortcode": "Ba.",
                    "unit": "µg/L",
                    "value": 0.0978,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "benzene": {
                    "found": true,
                    "name": "Benzene",
                    "shortcode": "Be.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "boron": {
                    "found": true,
                    "name": "Boron",
                    "shortcode": "Bo.",
                    "unit": "mg/L",
                    "value": 0.0429,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 7.8
                    }
                },
                "mercury": {
                    "found": true,
                    "name": "Mercury",
                    "shortcode": "Me.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tetrachloroethylene and trichloroethylene": {
                    "found": true,
                    "name": "Tetrachloroethylene and trichloroethylene",
                    "shortcode": "T.&T.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "thms": {
                    "found": true,
                    "name": "Trihalomethanes",
                    "shortcode": "THMs",
                    "unit": "µg/L",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 19.67
                    }
                },
                "ammonium": {
                    "found": true,
                    "name": "Ammonium",
                    "shortcode": "Am.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "sodium": {
                    "found": true,
                    "name": "Sodium",
                    "shortcode": "So.",
                    "unit": "mg/L",
                    "value": 16.7,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Low in minerals",
                        "value": 8.34
                    }
                },
                "sulphates": {
                    "found": true,
                    "name": "Sulphates",
                    "shortcode": "Su.",
                    "unit": "µg/L",
                    "value": 61.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "free_chlorine": {
                    "found": true,
                    "name": "Free chlorine",
                    "shortcode": "Chl. ",
                    "unit": "mg(Cl2)/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "chlorides": {
                    "found": true,
                    "name": "Chlorides",
                    "shortcode": "Ch.",
                    "unit": "mg/L",
                    "value": 35.1,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 8.5
                    }
                },
                "nitrites": {
                    "found": true,
                    "name": "Nitrites",
                    "shortcode": "Ni.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "manganese": {
                    "found": true,
                    "name": "Manganese",
                    "shortcode": "Ma.",
                    "unit": "µg/L",
                    "value": 0.96,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.19
                    }
                },
                "calcium": {
                    "found": true,
                    "name": "Calcium",
                    "shortcode": "Calc.",
                    "unit": "mg/L",
                    "value": 133,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Water rich in minerals. Not autorized for tap water but no risks for health.",
                        "value": 6.37
                    }
                },
                "conductivity": {
                    "found": true,
                    "name": "Conductivity",
                    "shortcode": "C.25°C",
                    "unit": "µS/cm (25°C)",
                    "value": 653,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 2.88
                    }
                },
                "magnesium": {
                    "found": true,
                    "name": "Magnesium",
                    "shortcode": "Mag.",
                    "unit": "mg/L",
                    "value": 5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with some minerals",
                        "value": 0.36
                    }
                },
                "hardness": {
                    "found": true,
                    "name": "Hardness of water",
                    "shortcode": "TH",
                    "unit": "°f",
                    "value": 31.5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with a very high lime concentration",
                        "value": 0.11
                    }
                },
                "turbidity": {
                    "found": true,
                    "name": "Turbidity",
                    "shortcode": "Tu.",
                    "unit": "NFU",
                    "value": 0.15,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.75
                    }
                },
                "ph": {
                    "found": true,
                    "name": "pH",
                    "shortcode": "pH",
                    "unit": "pH unity",
                    "value": 7.4,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Neutral",
                        "value": 1.8
                    }
                },
                "pcb": {
                    "found": true,
                    "name": "Polychlorinated biphenyl",
                    "shortcode": "PCB",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "temperature": {
                    "found": true,
                    "name": "Water temperature",
                    "shortcode": "W.T.",
                    "unit": "°C",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 4.38
                    }
                },
                "total_chlorine": {
                    "found": true,
                    "name": "Total chlorine",
                    "shortcode": "T.C.",
                    "unit": "mg(Cl2)/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 1.5
                    }
                },
                "coliform": {
                    "found": true,
                    "name": "Coliform bacteria/100mL",
                    "shortcode": "CB",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "coli": {
                    "found": true,
                    "name": "Escherichia coli",
                    "shortcode": "E.c",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "enterococci": {
                    "found": true,
                    "name": "Enterococci",
                    "shortcode": "Ent.",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "pahs": {
                    "found": true,
                    "name": "Toxic equivalent Polycyclic Aromatic Hydrocarbons (PAHs)",
                    "shortcode": "PAHs",
                    "unit": "µg/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Bad",
                        "icon": null,
                        "color": "#f26a01",
                        "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                        "value": 50
                    }
                },
                "acrylamide": {
                    "found": true,
                    "name": "Acrylamide",
                    "shortcode": "Ac.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "cadmium": {
                    "found": true,
                    "name": "Cadmium",
                    "shortcode": "Ca.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total chromium": {
                    "found": true,
                    "name": "Total chromium",
                    "shortcode": "Chr.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "nickel": {
                    "found": true,
                    "name": "Nickel",
                    "shortcode": "Nic.",
                    "unit": "µg/L",
                    "value": 3.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 17.88
                    }
                },
                "copper": {
                    "found": true,
                    "name": "Copper",
                    "shortcode": "Cop.",
                    "unit": "µg/L",
                    "value": 0.0901,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "bap": {
                    "found": true,
                    "name": "Benzo[a]pyrene",
                    "shortcode": "BaP",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tritium": {
                    "found": true,
                    "name": "Tritium",
                    "shortcode": "Tium.",
                    "unit": "Bq/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                }
            },
            "found": true,
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Bad",
                "icon": null,
                "color": "#f26a01",
                "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                "value": 50,
                "main_pollutants": [
                    "pahs"
                ]
            }
        },
        {
            "datetime": "2026-10-12T18:00:00Z",
            "pollutants": {
                "nitrates": {
                    "found": true,
                    "name": "Nitrates",
                    "shortcode": "N.",
                    "unit": "mg/L",
                    "value": 7.34,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 14.78
                    }
                },
                "pesticides": {
                    "found": true,
                    "name": "Total Pesticides",
                    "shortcode": "T.P.",
                    "unit": "µg/L",
                    "value": 0.187,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Moderate",
                        "icon": null,
                        "color": "#ffb121",
                        "description": "Water of which at least one parameter does not have the optimum concentration or value to guarantee very good quality. Water can still be consumed without risk.",
                        "value": 39.5
                    }
                },
                "arsenic": {
                    "found": true,
                    "name": "Arsenic",
                    "shortcode": "A.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "selenium": {
                    "found": true,
                    "name": "Selenium",
                    "shortcode": "S.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "bromates": {
                    "found": true,
                    "name": "Bromates",
                    "shortcode": "B.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 2,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total aluminium": {
                    "found": true,
                    "name": "Total Aluminium",
                    "shortcode": "Al.",
                    "unit": "µg/L",
                    "value": 4.2,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.21
                    }
                },
                "fluorides": {
                    "found": true,
                    "name": "Fluorides",
                    "shortcode": "Fl.",
                    "unit": "mg/L",
                    "value": 0.54,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Conservative for teeth",
                        "value": 0.2
                    }
                },
                "barium": {
                    "found": true,
                    "name": "Barium",
                    "shortcode": "Ba.",
                    "unit": "µg/L",
                    "value": 0.0978,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "benzene": {
                    "found": true,
                    "name": "Benzene",
                    "shortcode": "Be.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "boron": {
                    "found": true,
                    "name": "Boron",
                    "shortcode": "Bo.",
                    "unit": "mg/L",
                    "value": 0.0429,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 7.8
                    }
                },
                "mercury": {
                    "found": true,
                    "name": "Mercury",
                    "shortcode": "Me.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tetrachloroethylene and trichloroethylene": {
                    "found": true,
                    "name": "Tetrachloroethylene and trichloroethylene",
                    "shortcode": "T.&T.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "thms": {
                    "found": true,
                    "name": "Trihalomethanes",
                    "shortcode": "THMs",
                    "unit": "µg/L",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 19.67
                    }
                },
                "ammonium": {
                    "found": true,
                    "name": "Ammonium",
                    "shortcode": "Am.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "sodium": {
                    "found": true,
                    "name": "Sodium",
                    "shortcode": "So.",
                    "unit": "mg/L",
                    "value": 16.7,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Low in minerals",
                        "value": 8.34
                    }
                },
                "sulphates": {
                    "found": true,
                    "name": "Sulphates",
                    "shortcode": "Su.",
                    "unit": "µg/L",
                    "value": 61.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "free_chlorine": {
                    "found": true,
                    "name": "Free chlorine",
                    "shortcode": "Chl. ",
                    "unit": "mg(Cl2)/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "chlorides": {
                    "found": true,
                    "name": "Chlorides",
                    "shortcode": "Ch.",
                    "unit": "mg/L",
                    "value": 35.1,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 8.5
                    }
                },
                "nitrites": {
                    "found": true,
                    "name": "Nitrites",
                    "shortcode": "Ni.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "manganese": {
                    "found": true,
                    "name": "Manganese",
                    "shortcode": "Ma.",
                    "unit": "µg/L",
                    "value": 0.96,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.19
                    }
                },
                "calcium": {
                    "found": true,
                    "name": "Calcium",
                    "shortcode": "Calc.",
                    "unit": "mg/L",
                    "value": 133,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Water rich in minerals. Not autorized for tap water but no risks for health.",
                        "value": 6.37
                    }
                },
                "conductivity": {
                    "found": true,
                    "name": "Conductivity",
                    "shortcode": "C.25°C",
                    "unit": "µS/cm (25°C)",
                    "value": 653,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 2.88
                    }
                },
                "magnesium": {
                    "found": true,
                    "name": "Magnesium",
                    "shortcode": "Mag.",
                    "unit": "mg/L",
                    "value": 5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with some minerals",
                        "value": 0.36
                    }
                },
                "hardness": {
                    "found": true,
                    "name": "Hardness of water",
                    "shortcode": "TH",
                    "unit": "°f",
                    "value": 31.5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with a very high lime concentration",
                        "value": 0.11
                    }
                },
                "turbidity": {
                    "found": true,
                    "name": "Turbidity",
                    "shortcode": "Tu.",
                    "unit": "NFU",
                    "value": 0.15,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.75
                    }
                },
                "ph": {
                    "found": true,
                    "name": "pH",
                    "shortcode": "pH",
                    "unit": "pH unity",
                    "value": 7.4,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Neutral",
                        "value": 1.8
                    }
                },
                "pcb": {
                    "found": true,
                    "name": "Polychlorinated biphenyl",
                    "shortcode": "PCB",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "temperature": {
                    "found": true,
                    "name": "Water temperature",
                    "shortcode": "W.T.",
                    "unit": "°C",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 4.38
                    }
                },
                "total_chlorine": {
                    "found": true,
                    "name": "Total chlorine",
                    "shortcode": "T.C.",
                    "unit": "mg(Cl2)/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 1.5
                    }
                },
                "coliform": {
                    "found": true,
                    "name": "Coliform bacteria/100mL",
                    "shortcode": "CB",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "coli": {
                    "found": true,
                    "name": "Escherichia coli",
                    "shortcode": "E.c",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "enterococci": {
                    "found": true,
                    "name": "Enterococci",
                    "shortcode": "Ent.",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "pahs": {
                    "found": true,
                    "name": "Toxic equivalent Polycyclic Aromatic Hydrocarbons (PAHs)",
                    "shortcode": "PAHs",
                    "unit": "µg/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Bad",
                        "icon": null,
                        "color": "#f26a01",
                        "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                        "value": 50
                    }
                },
                "acrylamide": {
                    "found": true,
                    "name": "Acrylamide",
                    "shortcode": "Ac.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "cadmium": {
                    "found": true,
                    "name": "Cadmium",
                    "shortcode": "Ca.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total chromium": {
                    "found": true,
                    "name": "Total chromium",
                    "shortcode": "Chr.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "nickel": {
                    "found": true,
                    "name": "Nickel",
                    "shortcode": "Nic.",
                    "unit": "µg/L",
                    "value": 3.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 17.88
                    }
                },
                "copper": {
                    "found": true,
                    "name": "Copper",
                    "shortcode": "Cop.",
                    "unit": "µg/L",
                    "value": 0.0901,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "bap": {
                    "found": true,
                    "name": "Benzo[a]pyrene",
                    "shortcode": "BaP",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tritium": {
                    "found": true,
                    "name": "Tritium",
                    "shortcode": "Tium.",
                    "unit": "Bq/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                }
            },
            "found": true,
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Bad",
                "icon": null,
                "color": "#f26a01",
                "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                "value": 50,
                "main_pollutants": [
                    "pahs"
                ]
            }
        },
        {
            "datetime": "2026-10-12T19:00:00Z",
            "pollutants": {
                "nitrates": {
                    "found": true,
                    "name": "Nitrates",
                    "shortcode": "N.",
                    "unit": "mg/L",
                    "value": 7.34,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 14.78
                    }
                },
                "pesticides": {
                    "found": true,
                    "name": "Total Pesticides",
                    "shortcode": "T.P.",
                    "unit": "µg/L",
                    "value": 0.187,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Moderate",
                        "icon": null,
                        "color": "#ffb121",
                        "description": "Water of which at least one parameter does not have the optimum concentration or value to guarantee very good quality. Water can still be consumed without risk.",
                        "value": 39.5
                    }
                },
                "arsenic": {
                    "found": true,
                    "name": "Arsenic",
                    "shortcode": "A.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "selenium": {
                    "found": true,
                    "name": "Selenium",
                    "shortcode": "S.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "bromates": {
                    "found": true,
                    "name": "Bromates",
                    "shortcode": "B.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 2,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total aluminium": {
                    "found": true,
                    "name": "Total Aluminium",
                    "shortcode": "Al.",
                    "unit": "µg/L",
                    "value": 4.2,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.21
                    }
                },
                "fluorides": {
                    "found": true,
                    "name": "Fluorides",
                    "shortcode": "Fl.",
                    "unit": "mg/L",
                    "value": 0.54,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Conservative for teeth",
                        "value": 0.2
                    }
                },
                "barium": {
                    "found": true,
                    "name": "Barium",
                    "shortcode": "Ba.",
                    "unit": "µg/L",
                    "value": 0.0978,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "benzene": {
                    "found": true,
                    "name": "Benzene",
                    "shortcode": "Be.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "boron": {
                    "found": true,
                    "name": "Boron",
                    "shortcode": "Bo.",
                    "unit": "mg/L",
                    "value": 0.0429,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 7.8
                    }
                },
                "mercury": {
                    "found": true,
                    "name": "Mercury",
                    "shortcode": "Me.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tetrachloroethylene and trichloroethylene": {
                    "found": true,
                    "name": "Tetrachloroethylene and trichloroethylene",
                    "shortcode": "T.&T.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "thms": {
                    "found": true,
                    "name": "Trihalomethanes",
                    "shortcode": "THMs",
                    "unit": "µg/L",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 19.67
                    }
                },
                "ammonium": {
                    "found": true,
                    "name": "Ammonium",
                    "shortcode": "Am.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "sodium": {
                    "found": true,
                    "name": "Sodium",
                    "shortcode": "So.",
                    "unit": "mg/L",
                    "value": 16.7,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Low in minerals",
                        "value": 8.34
                    }
                },
                "sulphates": {
                    "found": true,
                    "name": "Sulphates",
                    "shortcode": "Su.",
                    "unit": "µg/L",
                    "value": 61.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "free_chlorine": {
                    "found": true,
                    "name": "Free chlorine",
                    "shortcode": "Chl. ",
                    "unit": "mg(Cl2)/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "chlorides": {
                    "found": true,
                    "name": "Chlorides",
                    "shortcode": "Ch.",
                    "unit": "mg/L",
                    "value": 35.1,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 8.5
                    }
                },
                "nitrites": {
                    "found": true,
                    "name": "Nitrites",
                    "shortcode": "Ni.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "manganese": {
                    "found": true,
                    "name": "Manganese",
                    "shortcode": "Ma.",
                    "unit": "µg/L",
                    "value": 0.96,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.19
                    }
                },
                "calcium": {
                    "found": true,
                    "name": "Calcium",
                    "shortcode": "Calc.",
                    "unit": "mg/L",
                    "value": 133,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Water rich in minerals. Not autorized for tap water but no risks for health.",
                        "value": 6.37
                    }
                },
                "conductivity": {
                    "found": true,
                    "name": "Conductivity",
                    "shortcode": "C.25°C",
                    "unit": "µS/cm (25°C)",
                    "value": 653,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 2.88
                    }
                },
                "magnesium": {
                    "found": true,
                    "name": "Magnesium",
                    "shortcode": "Mag.",
                    "unit": "mg/L",
                    "value": 5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with some minerals",
                        "value": 0.36
                    }
                },
                "hardness": {
                    "found": true,
                    "name": "Hardness of water",
                    "shortcode": "TH",
                    "unit": "°f",
                    "value": 31.5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with a very high lime concentration",
                        "value": 0.11
                    }
                },
                "turbidity": {
                    "found": true,
                    "name": "Turbidity",
                    "shortcode": "Tu.",
                    "unit": "NFU",
                    "value": 0.15,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.75
                    }
                },
                "ph": {
                    "found": true,
                    "name": "pH",
                    "shortcode": "pH",
                    "unit": "pH unity",
                    "value": 7.4,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Neutral",
                        "value": 1.8
                    }
                },
                "pcb": {
                    "found": true,
                    "name": "Polychlorinated biphenyl",
                    "shortcode": "PCB",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "temperature": {
                    "found": true,
                    "name": "Water temperature",
                    "shortcode": "W.T.",
                    "unit": "°C",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 4.38
                    }
                },
                "total_chlorine": {
                    "found": true,
                    "name": "Total chlorine",
                    "shortcode": "T.C.",
                    "unit": "mg(Cl2)/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 1.5
                    }
                },
                "coliform": {
                    "found": true,
                    "name": "Coliform bacteria/100mL",
                    "shortcode": "CB",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "coli": {
                    "found": true,
                    "name": "Escherichia coli",
                    "shortcode": "E.c",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "enterococci": {
                    "found": true,
                    "name": "Enterococci",
                    "shortcode": "Ent.",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "pahs": {
                    "found": true,
                    "name": "Toxic equivalent Polycyclic Aromatic Hydrocarbons (PAHs)",
                    "shortcode": "PAHs",
                    "unit": "µg/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Bad",
                        "icon": null,
                        "color": "#f26a01",
                        "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                        "value": 50
                    }
                },
                "acrylamide": {
                    "found": true,
                    "name": "Acrylamide",
                    "shortcode": "Ac.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "cadmium": {
                    "found": true,
                    "name": "Cadmium",
                    "shortcode": "Ca.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total chromium": {
                    "found": true,
                    "name": "Total chromium",
                    "shortcode": "Chr.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "nickel": {
                    "found": true,
                    "name": "Nickel",
                    "shortcode": "Nic.",
                    "unit": "µg/L",
                    "value": 3.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 17.88
                    }
                },
                "copper": {
                    "found": true,
                    "name": "Copper",
                    "shortcode": "Cop.",
                    "unit": "µg/L",
                    "value": 0.0901,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "bap": {
                    "found": true,
                    "name": "Benzo[a]pyrene",
                    "shortcode": "BaP",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tritium": {
                    "found": true,
                    "name": "Tritium",
                    "shortcode": "Tium.",
                    "unit": "Bq/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                }
            },
            "found": true,
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Bad",
                "icon": null,
                "color": "#f26a01",
                "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                "value": 50,
                "main_pollutants": [
                    "pahs"
                ]
            }
        },
        {
            "datetime": "2026-10-12T20:00:00Z",
            "pollutants": {
                "nitrates": {
                    "found": true,
                    "name": "Nitrates",
                    "shortcode": "N.",
                    "unit": "mg/L",
                    "value": 7.34,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 14.78
                    }
                },
                "pesticides": {
                    "found": true,
                    "name": "Total Pesticides",
                    "shortcode": "T.P.",
                    "unit": "µg/L",
                    "value": 0.187,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Moderate",
                        "icon": null,
                        "color": "#ffb121",
                        "description": "Water of which at least one parameter does not have the optimum concentration or value to guarantee very good quality. Water can still be consumed without risk.",
                        "value": 39.5
                    }
                },
                "arsenic": {
                    "found": true,
                    "name": "Arsenic",
                    "shortcode": "A.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "selenium": {
                    "found": true,
                    "name": "Selenium",
                    "shortcode": "S.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "bromates": {
                    "found": true,
                    "name": "Bromates",
                    "shortcode": "B.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 2,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total aluminium": {
                    "found": true,
                    "name": "Total Aluminium",
                    "shortcode": "Al.",
                    "unit": "µg/L",
                    "value": 4.2,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.21
                    }
                },
                "fluorides": {
                    "found": true,
                    "name": "Fluorides",
                    "shortcode": "Fl.",
                    "unit": "mg/L",
                    "value": 0.54,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Conservative for teeth",
                        "value": 0.2
                    }
                },
                "barium": {
                    "found": true,
                    "name": "Barium",
                    "shortcode": "Ba.",
                    "unit": "µg/L",
                    "value": 0.0978,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "benzene": {
                    "found": true,
                    "name": "Benzene",
                    "shortcode": "Be.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "boron": {
                    "found": true,
                    "name": "Boron",
                    "shortcode": "Bo.",
                    "unit": "mg/L",
                    "value": 0.0429,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 7.8
                    }
                },
                "mercury": {
                    "found": true,
                    "name": "Mercury",
                    "shortcode": "Me.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tetrachloroethylene and trichloroethylene": {
                    "found": true,
                    "name": "Tetrachloroethylene and trichloroethylene",
                    "shortcode": "T.&T.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "thms": {
                    "found": true,
                    "name": "Trihalomethanes",
                    "shortcode": "THMs",
                    "unit": "µg/L",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 19.67
                    }
                },
                "ammonium": {
                    "found": true,
                    "name": "Ammonium",
                    "shortcode": "Am.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "sodium": {
                    "found": true,
                    "name": "Sodium",
                    "shortcode": "So.",
                    "unit": "mg/L",
                    "value": 16.7,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Low in minerals",
                        "value": 8.34
                    }
                },
                "sulphates": {
                    "found": true,
                    "name": "Sulphates",
                    "shortcode": "Su.",
                    "unit": "µg/L",
                    "value": 61.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "free_chlorine": {
                    "found": true,
                    "name": "Free chlorine",
                    "shortcode": "Chl. ",
                    "unit": "mg(Cl2)/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "chlorides": {
                    "found": true,
                    "name": "Chlorides",
                    "shortcode": "Ch.",
                    "unit": "mg/L",
                    "value": 35.1,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 8.5
                    }
                },
                "nitrites": {
                    "found": true,
                    "name": "Nitrites",
                    "shortcode": "Ni.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "manganese": {
                    "found": true,
                    "name": "Manganese",
                    "shortcode": "Ma.",
                    "unit": "µg/L",
                    "value": 0.96,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.19
                    }
                },
                "calcium": {
                    "found": true,
                    "name": "Calcium",
                    "shortcode": "Calc.",
                    "unit": "mg/L",
                    "value": 133,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Water rich in minerals. Not autorized for tap water but no risks for health.",
                        "value": 6.37
                    }
                },
                "conductivity": {
                    "found": true,
                    "name": "Conductivity",
                    "shortcode": "C.25°C",
                    "unit": "µS/cm (25°C)",
                    "value": 653,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 2.88
                    }
                },
                "magnesium": {
                    "found": true,
                    "name": "Magnesium",
                    "shortcode": "Mag.",
                    "unit": "mg/L",
                    "value": 5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with some minerals",
                        "value": 0.36
                    }
                },
                "hardness": {
                    "found": true,
                    "name": "Hardness of water",
                    "shortcode": "TH",
                    "unit": "°f",
                    "value": 31.5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with a very high lime concentration",
                        "value": 0.11
                    }
                },
                "turbidity": {
                    "found": true,
                    "name": "Turbidity",
                    "shortcode": "Tu.",
                    "unit": "NFU",
                    "value": 0.15,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.75
                    }
                },
                "ph": {
                    "found": true,
                    "name": "pH",
                    "shortcode": "pH",
                    "unit": "pH unity",
                    "value": 7.4,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Neutral",
                        "value": 1.8
                    }
                },
                "pcb": {
                    "found": true,
                    "name": "Polychlorinated biphenyl",
                    "shortcode": "PCB",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "temperature": {
                    "found": true,
                    "name": "Water temperature",
                    "shortcode": "W.T.",
                    "unit": "°C",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 4.38
                    }
                },
                "total_chlorine": {
                    "found": true,
                    "name": "Total chlorine",
                    "shortcode": "T.C.",
                    "unit": "mg(Cl2)/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 1.5
                    }
                },
                "coliform": {
                    "found": true,
                    "name": "Coliform bacteria/100mL",
                    "shortcode": "CB",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "coli": {
                    "found": true,
                    "name": "Escherichia coli",
                    "shortcode": "E.c",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "enterococci": {
                    "found": true,
                    "name": "Enterococci",
                    "shortcode": "Ent.",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "pahs": {
                    "found": true,
                    "name": "Toxic equivalent Polycyclic Aromatic Hydrocarbons (PAHs)",
                    "shortcode": "PAHs",
                    "unit": "µg/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Bad",
                        "icon": null,
                        "color": "#f26a01",
                        "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                        "value": 50
                    }
                },
                "acrylamide": {
                    "found": true,
                    "name": "Acrylamide",
                    "shortcode": "Ac.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "cadmium": {
                    "found": true,
                    "name": "Cadmium",
                    "shortcode": "Ca.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total chromium": {
                    "found": true,
                    "name": "Total chromium",
                    "shortcode": "Chr.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "nickel": {
                    "found": true,
                    "name": "Nickel",
                    "shortcode": "Nic.",
                    "unit": "µg/L",
                    "value": 3.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 17.88
                    }
                },
                "copper": {
                    "found": true,
                    "name": "Copper",
                    "shortcode": "Cop.",
                    "unit": "µg/L",
                    "value": 0.0901,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "bap": {
                    "found": true,
                    "name": "Benzo[a]pyrene",
                    "shortcode": "BaP",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tritium": {
                    "found": true,
                    "name": "Tritium",
                    "shortcode": "Tium.",
                    "unit": "Bq/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                }
            },
            "found": true,
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Bad",
                "icon": null,
                "color": "#f26a01",
                "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                "value": 50,
                "main_pollutants": [
                    "pahs"
                ]
            }
        },
        {
            "datetime": "2026-10-12T21:00:00Z",
            "pollutants": {
                "nitrates": {
                    "found": true,
                    "name": "Nitrates",
                    "shortcode": "N.",
                    "unit": "mg/L",
                    "value": 7.34,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 14.78
                    }
                },
                "pesticides": {
                    "found": true,
                    "name": "Total Pesticides",
                    "shortcode": "T.P.",
                    "unit": "µg/L",
                    "value": 0.187,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Moderate",
                        "icon": null,
                        "color": "#ffb121",
                        "description": "Water of which at least one parameter does not have the optimum concentration or value to guarantee very good quality. Water can still be consumed without risk.",
                        "value": 39.5
                    }
                },
                "arsenic": {
                    "found": true,
                    "name": "Arsenic",
                    "shortcode": "A.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "selenium": {
                    "found": true,
                    "name": "Selenium",
                    "shortcode": "S.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "bromates": {
                    "found": true,
                    "name": "Bromates",
                    "shortcode": "B.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 2,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total aluminium": {
                    "found": true,
                    "name": "Total Aluminium",
                    "shortcode": "Al.",
                    "unit": "µg/L",
                    "value": 4.2,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.21
                    }
                },
                "fluorides": {
                    "found": true,
                    "name": "Fluorides",
                    "shortcode": "Fl.",
                    "unit": "mg/L",
                    "value": 0.54,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Conservative for teeth",
                        "value": 0.2
                    }
                },
                "barium": {
                    "found": true,
                    "name": "Barium",
                    "shortcode": "Ba.",
                    "unit": "µg/L",
                    "value": 0.0978,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "benzene": {
                    "found": true,
                    "name": "Benzene",
                    "shortcode": "Be.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "boron": {
                    "found": true,
                    "name": "Boron",
                    "shortcode": "Bo.",
                    "unit": "mg/L",
                    "value": 0.0429,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 7.8
                    }
                },
                "mercury": {
                    "found": true,
                    "name": "Mercury",
                    "shortcode": "Me.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tetrachloroethylene and trichloroethylene": {
                    "found": true,
                    "name": "Tetrachloroethylene and trichloroethylene",
                    "shortcode": "T.&T.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "thms": {
                    "found": true,
                    "name": "Trihalomethanes",
                    "shortcode": "THMs",
                    "unit": "µg/L",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 19.67
                    }
                },
                "ammonium": {
                    "found": true,
                    "name": "Ammonium",
                    "shortcode": "Am.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "sodium": {
                    "found": true,
                    "name": "Sodium",
                    "shortcode": "So.",
                    "unit": "mg/L",
                    "value": 16.7,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Low in minerals",
                        "value": 8.34
                    }
                },
                "sulphates": {
                    "found": true,
                    "name": "Sulphates",
                    "shortcode": "Su.",
                    "unit": "µg/L",
                    "value": 61.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "free_chlorine": {
                    "found": true,
                    "name": "Free chlorine",
                    "shortcode": "Chl. ",
                    "unit": "mg(Cl2)/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "chlorides": {
                    "found": true,
                    "name": "Chlorides",
                    "shortcode": "Ch.",
                    "unit": "mg/L",
                    "value": 35.1,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 8.5
                    }
                },
                "nitrites": {
                    "found": true,
                    "name": "Nitrites",
                    "shortcode": "Ni.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "manganese": {
                    "found": true,
                    "name": "Manganese",
                    "shortcode": "Ma.",
                    "unit": "µg/L",
                    "value": 0.96,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.19
                    }
                },
                "calcium": {
                    "found": true,
                    "name": "Calcium",
                    "shortcode": "Calc.",
                    "unit": "mg/L",
                    "value": 133,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Water rich in minerals. Not autorized for tap water but no risks for health.",
                        "value": 6.37
                    }
                },
                "conductivity": {
                    "found": true,
                    "name": "Conductivity",
                    "shortcode": "C.25°C",
                    "unit": "µS/cm (25°C)",
                    "value": 653,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 2.88
                    }
                },
                "magnesium": {
                    "found": true,
                    "name": "Magnesium",
                    "shortcode": "Mag.",
                    "unit": "mg/L",
                    "value": 5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with some minerals",
                        "value": 0.36
                    }
                },
                "hardness": {
                    "found": true,
                    "name": "Hardness of water",
                    "shortcode": "TH",
                    "unit": "°f",
                    "value": 31.5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with a very high lime concentration",
                        "value": 0.11
                    }
                },
                "turbidity": {
                    "found": true,
                    "name": "Turbidity",
                    "shortcode": "Tu.",
                    "unit": "NFU",
                    "value": 0.15,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.75
                    }
                },
                "ph": {
                    "found": true,
                    "name": "pH",
                    "shortcode": "pH",
                    "unit": "pH unity",
                    "value": 7.4,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Neutral",
                        "value": 1.8
                    }
                },
                "pcb": {
                    "found": true,
                    "name": "Polychlorinated biphenyl",
                    "shortcode": "PCB",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "temperature": {
                    "found": true,
                    "name": "Water temperature",
                    "shortcode": "W.T.",
                    "unit": "°C",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 4.38
                    }
                },
                "total_chlorine": {
                    "found": true,
                    "name": "Total chlorine",
                    "shortcode": "T.C.",
                    "unit": "mg(Cl2)/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 1.5
                    }
                },
                "coliform": {
                    "found": true,
                    "name": "Coliform bacteria/100mL",
                    "shortcode": "CB",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "coli": {
                    "found": true,
                    "name": "Escherichia coli",
                    "shortcode": "E.c",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "enterococci": {
                    "found": true,
                    "name": "Enterococci",
                    "shortcode": "Ent.",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "pahs": {
                    "found": true,
                    "name": "Toxic equivalent Polycyclic Aromatic Hydrocarbons (PAHs)",
                    "shortcode": "PAHs",
                    "unit": "µg/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Bad",
                        "icon": null,
                        "color": "#f26a01",
                        "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                        "value": 50
                    }
                },
                "acrylamide": {
                    "found": true,
                    "name": "Acrylamide",
                    "shortcode": "Ac.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "cadmium": {
                    "found": true,
                    "name": "Cadmium",
                    "shortcode": "Ca.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total chromium": {
                    "found": true,
                    "name": "Total chromium",
                    "shortcode": "Chr.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "nickel": {
                    "found": true,
                    "name": "Nickel",
                    "shortcode": "Nic.",
                    "unit": "µg/L",
                    "value": 3.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 17.88
                    }
                },
                "copper": {
                    "found": true,
                    "name": "Copper",
                    "shortcode": "Cop.",
                    "unit": "µg/L",
                    "value": 0.0901,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "bap": {
                    "found": true,
                    "name": "Benzo[a]pyrene",
                    "shortcode": "BaP",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tritium": {
                    "found": true,
                    "name": "Tritium",
                    "shortcode": "Tium.",
                    "unit": "Bq/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                }
            },
            "found": true,
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Bad",
                "icon": null,
                "color": "#f26a01",
                "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                "value": 50,
                "main_pollutants": [
                    "pahs"
                ]
            }
        },
        {
            "datetime": "2026-10-12T22:00:00Z",
            "pollutants": {
                "nitrates": {
                    "found": true,
                    "name": "Nitrates",
                    "shortcode": "N.",
                    "unit": "mg/L",
                    "value": 7.34,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 14.78
                    }
                },
                "pesticides": {
                    "found": true,
                    "name": "Total Pesticides",
                    "shortcode": "T.P.",
                    "unit": "µg/L",
                    "value": 0.187,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Moderate",
                        "icon": null,
                        "color": "#ffb121",
                        "description": "Water of which at least one parameter does not have the optimum concentration or value to guarantee very good quality. Water can still be consumed without risk.",
                        "value": 39.5
                    }
                },
                "arsenic": {
                    "found": true,
                    "name": "Arsenic",
                    "shortcode": "A.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "selenium": {
                    "found": true,
                    "name": "Selenium",
                    "shortcode": "S.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "bromates": {
                    "found": true,
                    "name": "Bromates",
                    "shortcode": "B.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 2,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total aluminium": {
                    "found": true,
                    "name": "Total Aluminium",
                    "shortcode": "Al.",
                    "unit": "µg/L",
                    "value": 4.2,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.21
                    }
                },
                "fluorides": {
                    "found": true,
                    "name": "Fluorides",
                    "shortcode": "Fl.",
                    "unit": "mg/L",
                    "value": 0.54,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Conservative for teeth",
                        "value": 0.2
                    }
                },
                "barium": {
                    "found": true,
                    "name": "Barium",
                    "shortcode": "Ba.",
                    "unit": "µg/L",
                    "value": 0.0978,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "benzene": {
                    "found": true,
                    "name": "Benzene",
                    "shortcode": "Be.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "boron": {
                    "found": true,
                    "name": "Boron",
                    "shortcode": "Bo.",
                    "unit": "mg/L",
                    "value": 0.0429,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 7.8
                    }
                },
                "mercury": {
                    "found": true,
                    "name": "Mercury",
                    "shortcode": "Me.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tetrachloroethylene and trichloroethylene": {
                    "found": true,
                    "name": "Tetrachloroethylene and trichloroethylene",
                    "shortcode": "T.&T.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "thms": {
                    "found": true,
                    "name": "Trihalomethanes",
                    "shortcode": "THMs",
                    "unit": "µg/L",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 19.67
                    }
                },
                "ammonium": {
                    "found": true,
                    "name": "Ammonium",
                    "shortcode": "Am.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "sodium": {
                    "found": true,
                    "name": "Sodium",
                    "shortcode": "So.",
                    "unit": "mg/L",
                    "value": 16.7,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Low in minerals",
                        "value": 8.34
                    }
                },
                "sulphates": {
                    "found": true,
                    "name": "Sulphates",
                    "shortcode": "Su.",
                    "unit": "µg/L",
                    "value": 61.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "free_chlorine": {
                    "found": true,
                    "name": "Free chlorine",
                    "shortcode": "Chl. ",
                    "unit": "mg(Cl2)/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": null,
                        "color": "#9A9A9A",
                        "description": null,
                        "value": null
                    }
                },
                "chlorides": {
                    "found": true,
                    "name": "Chlorides",
                    "shortcode": "Ch.",
                    "unit": "mg/L",
                    "value": 35.1,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 8.5
                    }
                },
                "nitrites": {
                    "found": true,
                    "name": "Nitrites",
                    "shortcode": "Ni.",
                    "unit": "mg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "manganese": {
                    "found": true,
                    "name": "Manganese",
                    "shortcode": "Ma.",
                    "unit": "µg/L",
                    "value": 0.96,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.19
                    }
                },
                "calcium": {
                    "found": true,
                    "name": "Calcium",
                    "shortcode": "Calc.",
                    "unit": "mg/L",
                    "value": 133,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Water rich in minerals. Not autorized for tap water but no risks for health.",
                        "value": 6.37
                    }
                },
                "conductivity": {
                    "found": true,
                    "name": "Conductivity",
                    "shortcode": "C.25°C",
                    "unit": "µS/cm (25°C)",
                    "value": 653,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 2.88
                    }
                },
                "magnesium": {
                    "found": true,
                    "name": "Magnesium",
                    "shortcode": "Mag.",
                    "unit": "mg/L",
                    "value": 5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with some minerals",
                        "value": 0.36
                    }
                },
                "hardness": {
                    "found": true,
                    "name": "Hardness of water",
                    "shortcode": "TH",
                    "unit": "°f",
                    "value": 31.5,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water with a very high lime concentration",
                        "value": 0.11
                    }
                },
                "turbidity": {
                    "found": true,
                    "name": "Turbidity",
                    "shortcode": "Tu.",
                    "unit": "NFU",
                    "value": 0.15,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0.75
                    }
                },
                "ph": {
                    "found": true,
                    "name": "pH",
                    "shortcode": "pH",
                    "unit": "pH unity",
                    "value": 7.4,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Neutral",
                        "value": 1.8
                    }
                },
                "pcb": {
                    "found": true,
                    "name": "Polychlorinated biphenyl",
                    "shortcode": "PCB",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "temperature": {
                    "found": true,
                    "name": "Water temperature",
                    "shortcode": "W.T.",
                    "unit": "°C",
                    "value": 22,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 4.38
                    }
                },
                "total_chlorine": {
                    "found": true,
                    "name": "Total chlorine",
                    "shortcode": "T.C.",
                    "unit": "mg(Cl2)/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 1.5
                    }
                },
                "coliform": {
                    "found": true,
                    "name": "Coliform bacteria/100mL",
                    "shortcode": "CB",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "coli": {
                    "found": true,
                    "name": "Escherichia coli",
                    "shortcode": "E.c",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "enterococci": {
                    "found": true,
                    "name": "Enterococci",
                    "shortcode": "Ent.",
                    "unit": "/100mL",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "pahs": {
                    "found": true,
                    "name": "Toxic equivalent Polycyclic Aromatic Hydrocarbons (PAHs)",
                    "shortcode": "PAHs",
                    "unit": "µg/L",
                    "value": 0.06,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Bad",
                        "icon": null,
                        "color": "#f26a01",
                        "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                        "value": 50
                    }
                },
                "acrylamide": {
                    "found": true,
                    "name": "Acrylamide",
                    "shortcode": "Ac.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "cadmium": {
                    "found": true,
                    "name": "Cadmium",
                    "shortcode": "Ca.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "total chromium": {
                    "found": true,
                    "name": "Total chromium",
                    "shortcode": "Chr.",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "nickel": {
                    "found": true,
                    "name": "Nickel",
                    "shortcode": "Nic.",
                    "unit": "µg/L",
                    "value": 3.9,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 17.88
                    }
                },
                "copper": {
                    "found": true,
                    "name": "Copper",
                    "shortcode": "Cop.",
                    "unit": "µg/L",
                    "value": 0.0901,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Satisfying",
                        "icon": null,
                        "color": "#adc704",
                        "description": "Good quality water to drink without moderation.",
                        "value": 5
                    }
                },
                "bap": {
                    "found": true,
                    "name": "Benzo[a]pyrene",
                    "shortcode": "BaP",
                    "unit": "µg/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                },
                "tritium": {
                    "found": true,
                    "name": "Tritium",
                    "shortcode": "Tium.",
                    "unit": "Bq/L",
                    "value": 0,
                    "confidence": 5,
                    "index": {
                        "index_type": "meersens",
                        "index_name": "Meersens",
                        "qualification": "Good",
                        "icon": null,
                        "color": "#05b3a4",
                        "description": "Water of very good quality to consume without moderation.",
                        "value": 0
                    }
                }
            },
            "found": true,
            "index": {
                "index_type": "meersens",
                "index_name": "Meersens",
                "qualification": "Bad",
                "icon": null,
                "color": "#f26a01",
                "description": "Water in which one parameter may exceed the fixed quality reference. The water can be consumed but its quality is not optimal. If in doubt, contact your water supplier or city officials.",
                "value": 50,
                "main_pollutants": [
                    "pahs"
                ]
            }
        }
    ],
    "page": {
        "totalElements": 24,
        "totalPages": 4,
        "pageNumber": 1,
        "size": 6
    }
}
'''

# Metadados de EXEMPLO FIXO
metadata = {
    "contract_version": "1.0",
    "source": {"type": "api", "provider": "meersens"},
    "ingestion_datetime": "2026-10-14T18:22:00Z",
    "station": {
        "code": "FR_PARIS_488566_23522",
        "name": "Estação Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
    },
}

# Chamada para método de Construção dos documentos bronze para parâmetros de água
documents = build_bronze_documents_water(meersens_json, metadata, allowed_parameters)
# Impressão do documento bronze construído usando dump JSON para melhor visualização na tela
print(json.dumps(documents, indent=2, ensure_ascii=False))
