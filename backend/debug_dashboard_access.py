
import httpx
import time

def test_dashboard_access():
    base_url = "http://localhost:8000"
    email = "kesav4niq@gmail.com"
    password = "password123"

    with httpx.Client(base_url=base_url, timeout=10) as client:
        # 1. Login
        print(f"Logging in as {email}...")
        try:
            resp = client.post("/auth/login", json={"email": email, "password": password})
            print(f"Login Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Login Failed: {resp.text}")
                return
            
            token_data = resp.json()
            access_token = token_data["access_token"]
            print(f"Got Access Token: {access_token[:20]}...")
            
            # 2. Access Dashboard Endpoint
            print("\nAccessing /api/financial/summary...")
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = client.get("/api/financial/summary", headers=headers)
            print(f"Summary Status: {resp.status_code}")
            print(f"Summary Response: {resp.text}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_dashboard_access()
