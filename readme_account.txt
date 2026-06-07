Yoko CatCut Account Guide
========================

Default Account
---------------

- Account: default-user
- Password: yoko1234
- Account file: workspace/.system/accounts/users.json

The default account is created automatically when the backend starts for the
first time. It is approved by default and does not require a lock file.


Account Registration
--------------------

1. Open the login page.
2. Click "계정 등록".
3. Enter an account name and a password of at least 8 characters.
4. Submit the form.
5. The backend creates the account folder:

   workspace/{account}/

6. The backend also creates this approval lock file:

   workspace/{account}/lock.lck

7. The new account cannot log in while lock.lck exists.
8. To approve login for that account, delete lock.lck.
9. After approval, log in with the registered account and password.


Account Isolation
-----------------

- Each account can only manage its own projects.
- Project data is stored under workspace/{account}/.
- Uploads, jobs, subtitles, exports, and media URLs require the account token.
- The account/password registry is stored in:

  workspace/.system/accounts/users.json


Operational Notes
-----------------

- Do not commit workspace/.system/accounts/users.json to Git.
- Do not commit any lock.lck files to Git.
- If an account must be blocked again, create workspace/{account}/lock.lck.
- If the default password is still in use, change it in the account file before
  exposing the service on a shared network.
