#! /bin/sh

echo -e "\n Running gunicorn as daemon for tests:\n$(
    gunicorn --bind="0.0.0.0:5000" --daemon app:api
)"

sleep 4

echo "Running e2e tests"
echo -e "\n E2e tests finished:\n$(
    resttest.py http://127.0.0.1:5000 tests/test.yaml
)"

echo " Running trezor tests"
echo -e "\n Trezor tests finished:\n$(
    pytest tests/test_trezor.py
)"

echo " Running parsing tests"
echo -e "\n Parsing tests finished:\n$(
    pytest tests/test_parsing.py
)"

pkill -f gunicorn

echo " Running gunicorn:"

gunicorn --bind="0.0.0.0:5000" app:api
