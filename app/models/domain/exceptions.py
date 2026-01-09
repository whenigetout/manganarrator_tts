from pydantic import BaseModel

class TTSSynthesisError(Exception):
    pass

class TTSInputError(Exception):
    pass

class EnvError(Exception):
    pass