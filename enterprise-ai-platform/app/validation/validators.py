from app.core.schemas import ValidationResult


class SchemaValidator:
    def validate(
        self, category: str, output: str, required_fields: list[str] | None = None
    ) -> ValidationResult:
        errors = []
        if not output.strip():
            errors.append("output is empty")
        if required_fields:
            missing = [field for field in required_fields if field not in output]
            if missing:
                errors.append(f"missing required fields: {', '.join(missing)}")
        return ValidationResult(valid=not errors, errors=errors)
