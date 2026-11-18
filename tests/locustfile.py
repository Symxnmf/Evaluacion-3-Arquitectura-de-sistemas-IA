from locust import HttpUser, between, task


class ShopFastUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        response = self.client.post("/auth/token")
        self.token = response.json().get("access_token", "")

    @task
    def recommendations(self):
        self.client.get(
            "/recommendations/1",
            headers={"Authorization": f"Bearer {self.token}"},
            name="/recommendations/{user_id}",
        )
