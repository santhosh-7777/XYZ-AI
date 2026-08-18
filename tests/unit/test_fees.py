from backend.app.services.fees import FeeService
from backend.app.tools.fees import FeeTool


def test_get_fees():
    result = FeeService.get_fees(1)

    assert result["user_id"] == 1
    assert result["total_fees"] == 75000.0
    assert result["paid_amount"] == 60000.0
    assert result["pending_amount"] == 15000.0
    assert result["currency"] == "INR"
    assert result["status"] == "PARTIALLY_PAID"


def test_fee_tool():
    result = FeeTool.execute(1)

    assert result["user_id"] == 1
    assert result["pending_amount"] == 15000.0