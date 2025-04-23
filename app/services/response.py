from typing import List, Dict, Any, Optional, Union


class Error:
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code

    def to_dict(self) -> Dict[str, str]:
        error_dict = {"message": self.message}
        if self.code:
            error_dict["code"] = self.code
        return error_dict


class Response:
    def __init__(self):
        self.status_code: int = 200
        self.errors: List[Error] = []
        self.payload: Dict[str, Any] = {}
        self.success: bool = False

    def add_error(self, error: Error) -> None:
        self.errors.append(error)

    def add_errors(self, errors: List[Error]) -> None:
        if errors:
            self.errors.extend(errors)

    def set_status_code(self, status_code: int) -> None:
        self.status_code = status_code

    def set_payload(self, payload: Dict[str, Any]) -> None:
        self.payload = payload

    def get_response(self) -> Dict[str, Any]:
        if not self.errors:
            self.status_code = self.status_code if self.status_code != 500 else 200
            self.success = True
        else:
            self.status_code = self.status_code if self.status_code != 200 else 500
            self.success = False

        return {
            "statusCode": self.status_code,
            "errors": [error.to_dict() for error in self.errors],
            "payload": self.payload,
            "success": self.success
        }
