from models.lpar import LPARConfig

LPAR_CONFIGS = [
    LPARConfig("PROD01", 16, 64, "online", [8, 9, 10, 14, 15, 16]),
    LPARConfig("PROD02", 12, 48, "online", [8, 9, 10, 14, 15, 16]),
    LPARConfig("BATCH01", 8, 32, "batch", [22, 23, 0, 1, 2, 3, 4, 5]),
    LPARConfig("TEST01", 4, 16, "mixed", [9, 10, 11, 15, 16, 17]),
]

SYSPLEX_NAME = "SYSPLEX01"
