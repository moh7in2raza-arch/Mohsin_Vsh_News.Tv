def handle_login(self):

    username = self.username.text().strip()
    password = self.password.text()

    try:

        self.auth_service.login(
            username,
            password,
        )

        QMessageBox.information(
            self,
            "Success",
            "Login successful",
        )

    except AuthError as ex:

        QMessageBox.warning(
            self,
            "Login Failed",
            str(ex),
        )

         