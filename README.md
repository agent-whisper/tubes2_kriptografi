# tubes2_kriptografi
## Tugas Besar 2: Tanda tangan digital

- M. Umar Fariz Tumbuan / 13515050
- M. Treza Norlandra / 13515080
- Diki Ardian Wirasandi / 13515092

*NOTES:*

- We are using urllib3 for testing purposes. Remove it if not required anymore
- To reduce inbox/outbox query load during testing, the client will filter email with 'kripto' in subject

How to run:
1. Install the requirements or create a virtual environment for Python 3
2. Create client secret for authorization from OAuth 2.0.

If running locally for testing:

3. Open ```127.0.0.1:5000``` in your browser
4. Change to responsive design mode (F12)

If planning to deploy:

5. Set the config.yml for your public ip and port
6. Make sure that google authorized your domain
7. Make sure the ip and port is accessible from outside.

8. Run the server with ```python3 run.py```

Note: requires instance/app_credentials.json (from google developer console; not included) for google authentication.
