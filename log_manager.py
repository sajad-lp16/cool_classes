import os
import enum
from datetime import datetime

from django.conf import settings


class LogMessages(enum.Enum):
    # ----------------------------------------------- SUCCESSFUL -------------------------------------------------------
    SUCCESSFUL_DIRECT_CHARGE = (
        "INFO-{datetime}-package[PACKAGE_ID={package_id}], direct charge was applied successfully for "
        "user[MOBILE={mobile}], "
        "amount[AMOUNT={price}], "
        "transaction[TRANSACTION_ID={transaction_id}], "
        "operator[OPERATOR_ID={operator}], "
        "result[RESULT_CODE={result_code}]")

    SUCCESSFUL_PACKAGE = (
        "INFO-{datetime}-package[PACKAGE_ID={package_id}], internet package was applied successfully for "
        "user[MOBILE={mobile}], "
        "amount[AMOUNT={price}], "
        "transaction[TRANSACTION_ID={transaction_id}], "
        "operator[OPERATOR_ID={operator}], "
        "result[RESULT_CODE={result_code}]")

    # ------------------------------------------------- FAIL -----------------------------------------------------------
    FAIL_DIRECT_CHARGE = (
        "ERROR-{datetime}-package[PACKAGE_ID={package_id}], direct charge was failed for "
        "user[MOBILE={mobile}], "
        "amount[AMOUNT={price}], "
        "transaction[TRANSACTION_ID={transaction_id}], "
        "operator[OPERATOR_ID={operator}], "
        "ERROR=> {result_code}")

    FAIL_PACKAGE = (
        "ERROR-{datetime}-package[PACKAGE_ID={package_id}], internet package was failed for "
        "user[MOBILE={mobile}], "
        "amount[AMOUNT={price}], "
        "transaction[TRANSACTION_ID={transaction_id}], "
        "operator[OPERATOR_ID={operator}], "
        "ERROR =>[RESULT_CODE={result_code}]")

    CONNECTION_ERROR = """ERROR-{datetime}-connection error ERROR={error}"""


class LogManager:
    _LOGS_DIR = settings.BASE_DIR / "logs"

    # ---------------------------------------------- HIDDEN METHODS ----------------------------------------------------
    @classmethod
    def _perform_write_log(cls, filename: str, data: str) -> None:
        with open(cls._LOGS_DIR / filename, "a") as file:
            file.write(data)

    @classmethod
    def _write_successful_direct_charge_log(cls, log_data: dict) -> None:
        filename = f"direct_{datetime.now().date().__str__()}_{os.getpid()}.log"
        message = LogMessages.SUCCESSFUL_DIRECT_CHARGE.value.format(**log_data)
        cls._perform_write_log(filename, message)

    @classmethod
    def _write_fail_direct_charge_log(cls, log_data: dict) -> None:
        filename = f"direct_{datetime.now().date().__str__()}_{os.getpid()}_err.log"
        message = LogMessages.FAIL_DIRECT_CHARGE.value.format(**log_data)
        cls._perform_write_log(filename, message)

    @classmethod
    def _write_successful_package_log(cls, log_data: dict) -> None:
        filename = f"package_{datetime.now().date().__str__()}_{os.getpid()}.log"
        message = LogMessages.SUCCESSFUL_PACKAGE.value.format(**log_data)
        cls._perform_write_log(filename, message)

    @classmethod
    def _write_fail_package_log(cls, log_data: dict) -> None:
        filename = f"package_{datetime.now().date().__str__()}_{os.getpid()}_err.log"
        message = LogMessages.FAIL_PACKAGE.value.format(**log_data)
        cls._perform_write_log(filename, message)

    # ------------------------------------------ ACCESSIBLE METHODS ----------------------------------------------------
    @classmethod
    def write_connection_error_log(cls, log_data: str) -> None:
        filename = f"connection_{datetime.now().date().__str__()}_err.log"
        message = LogMessages.CONNECTION_ERROR.value.format(
            datetime=datetime.now(),
            error=log_data
        )
        cls._perform_write_log(filename, message)

    @classmethod
    def write_purchase_log(cls, log_data: dict) -> None:
        log_data.update({
            "datetime": datetime.now()
        })
        if log_data.pop("is_package"):
            if log_data.get("status") == 1:
                return cls._write_successful_package_log(log_data)
            return cls._write_fail_package_log(log_data)
        if log_data.get("status") == 1:
            return cls._write_successful_direct_charge_log(log_data)
        return cls._write_fail_direct_charge_log(log_data)

