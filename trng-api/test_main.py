from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.content.decode() == '"pong"'


def test_list_devices():
    response = client.get("/list_devices")
    assert response.status_code == 200
    assert isinstance(response.json(), str)

def test_get_random_nrs():
    dtypes = ["byte", "ubyte", "short", "ushort", "intc", "uintc", "int_", "uint", "longlong", "ulonglong",
              "half", "float16", "single", "double"]
    n_numbers = 10
    for dtype in dtypes:
        response = client.post("/get_random_nrs", data={"dtype": dtype, "n_numbers": n_numbers})
        results = response.json()
        assert response.status_code == 200
        assert isinstance(results, dict)
        assert "length" in results
        assert "actual_length" in results
        assert "dtype" in results
        assert len(results["data"]) == n_numbers
        assert "device" in results


def test_get_random_hex():
    response = client.post("/get_random_hex", data={"length": 100})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
