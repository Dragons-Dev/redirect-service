import requests
import urllib3

urllib3.disable_warnings()  # to suppress the `verify=False` statement in every request. best I've found so far 


class RedirectRequest:
    def __init__(self, url: str, session: requests.Session, secret: str):
        self.url = url
        self.session = session
        self.secret = secret
        self.headers = {"User-agent": "Dragons_RedirectWrapper 1.0.1"}

    def get_redirect(self, redirect_name: str, allow_redirects: bool = True):
        return self.session.get(f"{self.url}/api/get_redirect/{redirect_name}", verify=False, headers=self.headers)

    def add_redirect(self, redirect_name: str, redirect_value: str, allow_redirects: bool = True):
        return self.session.post(
            f"{self.url}/api/add_redirect",
            json={
                "name": redirect_name,
                "value": redirect_value,
                "secret": self.secret,
            },
            verify=False,
            headers=self.headers,
        )

    def update_redirect(self, redirect_name: str, redirect_value: str, allow_redirects: bool = True):
        return self.session.put(
            f"{self.url}/api/update_redirect/{redirect_name}",
            json={
                "name": redirect_name,
                "value": redirect_value,
                "secret": self.secret,
            },
            verify=False,
            headers=self.headers,
        )

    def remove_redirect(self, redirect_name: str, allow_redirects: bool = True):
        return self.session.delete(
            f"{self.url}/api/remove_redirect",
            json={"name": redirect_name, "value": "", "secret": self.secret},
            verify=False,
            headers=self.headers,
        )


if __name__ == "__main__":
    main = RedirectRequest("https://your.redirect.example.com", requests.Session(), "SOME_SUPER_SECURE_SECRET")
    assert main.add_redirect("test", "https://127.0.0.1:8000/super_secret_route").status_code == 200
    assert main.update_redirect("test", "https://127.0.0.1:8000/test").status_code == 200
    assert main.get_redirect("test").status_code == 200
    assert main.remove_redirect("test").status_code == 200
