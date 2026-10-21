from dataclasses import dataclass


@dataclass
class Operator:
    id: int
    user_id: int | None = None
    service_id: int | None = None

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError(
                "O identificador do operador deve ser maior que zero."
            )
        if (self.user_id is None) == (self.service_id is None):
            raise ValueError(
                "O operador deve estar associado a um usuário ou a um serviço, mas não aos dois."
            )