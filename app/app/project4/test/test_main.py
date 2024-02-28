from fastapi.testclient import TestClient
import main
from httpx import Response
from fastapi import status

client = TestClient(main.app)


def test_return_health_check():
    response: Response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Healthy"}
