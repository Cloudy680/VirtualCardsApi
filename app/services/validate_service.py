import re

from fastapi import HTTPException


class ValidationService:

    @staticmethod
    async def validate_password(password: str):
        has_lower = re.search(r'[a-z]', password) is not None
        has_upper = re.search(r'[A-Z]', password) is not None
        has_digit = re.search(r'\d', password) is not None
        has_special = re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', password) is not None
        password_check = {"small letter": has_lower, "capital letter": has_upper, "digit": has_digit,
                          "special symbol": has_special}
        for key in password_check:
            if not password_check[key]:
                raise HTTPException(status_code=400, detail=password_check)

    @staticmethod
    async def validate_card_by_luna_algorithm(card_number : str):
        card_to_check = list(card_number)
        card_to_check.reverse()
        odd = 0
        even = 0
        for i in range(len(card_to_check)):
            if (i + 1) % 2 != 0:
                odd +=  int(card_to_check[i])
            else:
                temp = int(card_to_check[i]) * 2
                while temp > 0:
                    even += temp % 10
                    temp //= 10

        if (odd + even) % 10 == 0:
            return True
        else:
            return False

validate_service_obj = ValidationService()