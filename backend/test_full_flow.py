
import httpx
import time
import sys

def test_full_flow():
    base_url = "http://localhost:8000"
    # Unique email to ensure clean run
    email = f"flow_test_{int(time.time())}@example.com"
    password = "FlowPassword123!"
    
    with httpx.Client(base_url=base_url, timeout=10) as client:
        print(f"--- 1. REGISTER: {email} ---")
        try:
            reg_resp = client.post("/auth/register", json={
                "email": email,
                "password": password,
                "company_name": "Flow Corp",
                "industry_type": "services"  # lowercase enum
            })
            print(f"Register Status: {reg_resp.status_code}")
            if reg_resp.status_code != 201:
                print(f"Register Failed: {reg_resp.text}")
                return
            user_id = reg_resp.json()["id"]
            print(f"Registered User ID: {user_id}")
            
            print(f"\n--- 2. LOGIN ---")
            # Note: API expects JSON body as per previous check (UserLogin schema)
            # Confirmed in auth.py: login(credentials: UserLogin)
            login_resp = client.post("/auth/login", json={
                "email": email,
                "password": password
            })
            print(f"Login Status: {login_resp.status_code}")
            if login_resp.status_code != 200:
                print(f"Login Failed: {login_resp.text}")
                return
                
            token_data = login_resp.json()
            access_token = token_data["access_token"]
            print(f"Access Token: {access_token[:20]}...")
            
            print(f"\n--- 3. ACCESS DASHBOARD (Financial Summary) ---")
            headers = {"Authorization": f"Bearer {access_token}"}
            dash_resp = client.get("/api/financial/summary", headers=headers)
            print(f"Dashboard Status: {dash_resp.status_code}")
            # 404 is ACCEPTABLE here because we have no data, but 401 is FAIL
            if dash_resp.status_code == 401:
                print("FAIL: Dashboard returned 401 Unauthorized!")
                print(f"Response: {dash_resp.text}")
            elif dash_resp.status_code == 404:
                print("SUCCESS: Dashboard returned 404 (No Data), which is expected for new user.")
            elif dash_resp.status_code == 200:
                print("SUCCESS: Dashboard returned 200.")
            else:
                print(f"Unexpected Status: {dash_resp.status_code}")
                print(f"Response: {dash_resp.text}")
                
        except Exception as e:
            print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_full_flow()
