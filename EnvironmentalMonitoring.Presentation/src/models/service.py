from dataclasses import dataclass

@dataclass
class Service:
    id: int
    name: str
    code: str
    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError(
                "O identificador do serviço deve ser maior que zero."
            )        
        if not self.code or not self.code.strip():
            raise ValueError(
                "O código do serviço não pode estar vazio."
            )        